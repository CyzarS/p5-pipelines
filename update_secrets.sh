#!/bin/bash

# Script para actualizar secrets de GitHub con credenciales de AWS Academy
# Requiere GitHub CLI (gh) instalado y autenticado

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Actualizador de Secrets para GitHub - AWS Academy    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Verificar si gh CLI está instalado
if ! command -v gh &> /dev/null; then
    echo -e "${RED}Error: GitHub CLI (gh) no está instalado${NC}"
    echo ""
    echo "Instalar GitHub CLI:"
    echo "  macOS:   brew install gh"
    echo "  Linux:   https://github.com/cli/cli/blob/trunk/docs/install_linux.md"
    echo "  Windows: https://github.com/cli/cli/releases"
    echo ""
    exit 1
fi

# Verificar autenticación
if ! gh auth status &> /dev/null; then
    echo -e "${RED}No estás autenticado en GitHub CLI${NC}"
    echo ""
    echo "Ejecuta primero: gh auth login"
    echo ""
    exit 1
fi

echo -e "${GREEN}✓ GitHub CLI instalado y autenticado${NC}"
echo ""

# Obtener repositorio actual
REPO=$(git remote get-url origin 2>/dev/null | sed 's/.*github.com[:/]\(.*\)\.git/\1/')

if [ -z "$REPO" ]; then
    echo -e "${RED}Error: No se pudo detectar el repositorio de GitHub${NC}"
    echo "Asegúrate de estar en un directorio con repositorio Git configurado"
    exit 1
fi

echo -e "${BLUE}Repositorio detectado: ${YELLOW}$REPO${NC}"
echo ""

# Menú de opciones
echo "¿Qué secrets deseas actualizar?"
echo ""
echo "  1) Solo credenciales de AWS Academy (recomendado)"
echo "  2) Todas las credenciales (AWS + EC2 + Docker Hub)"
echo "  3) Solo Docker Hub"
echo "  4) Solo EC2"
echo ""
read -p "Selecciona una opción (1-4): " OPTION

case $OPTION in
    1)
        echo ""
        echo -e "${YELLOW}Actualizando credenciales de AWS Academy...${NC}"
        echo ""
        echo "Ve a AWS Academy y copia las credenciales:"
        echo "  1. AWS Details → Show"
        echo "  2. Copia cada valor cuando se solicite"
        echo ""
        
        read -p "aws_access_key_id = " AWS_ACCESS_KEY_ID
        read -p "aws_secret_access_key = " AWS_SECRET_ACCESS_KEY
        read -p "aws_session_token = " AWS_SESSION_TOKEN
        
        if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ] || [ -z "$AWS_SESSION_TOKEN" ]; then
            echo -e "${RED}Error: Todas las credenciales son requeridas${NC}"
            exit 1
        fi
        
        echo ""
        echo "Actualizando secrets en GitHub..."
        gh secret set AWS_ACCESS_KEY_ID --body "$AWS_ACCESS_KEY_ID" --repo "$REPO"
        gh secret set AWS_SECRET_ACCESS_KEY --body "$AWS_SECRET_ACCESS_KEY" --repo "$REPO"
        gh secret set AWS_SESSION_TOKEN --body "$AWS_SESSION_TOKEN" --repo "$REPO"
        
        echo ""
        echo -e "${GREEN}✓ Credenciales de AWS actualizadas exitosamente${NC}"
        ;;
        
    2)
        echo ""
        echo -e "${YELLOW}Actualizando todas las credenciales...${NC}"
        echo ""
        
        # AWS
        echo "=== Credenciales de AWS Academy ==="
        read -p "aws_access_key_id = " AWS_ACCESS_KEY_ID
        read -p "aws_secret_access_key = " AWS_SECRET_ACCESS_KEY
        read -p "aws_session_token = " AWS_SESSION_TOKEN
        
        # Docker Hub
        echo ""
        echo "=== Docker Hub ==="
        read -p "DOCKERHUB_USERNAME = " DOCKERHUB_USERNAME
        read -sp "DOCKERHUB_TOKEN = " DOCKERHUB_TOKEN
        echo ""
        
        # EC2
        echo ""
        echo "=== EC2 ==="
        read -p "EC2_HOST (IP pública) = " EC2_HOST
        read -p "EC2_USER (default: ec2-user) = " EC2_USER
        EC2_USER=${EC2_USER:-ec2-user}
        
        echo ""
        echo "Para EC2_SSH_KEY, pega el contenido COMPLETO de tu archivo .pem"
        echo "Presiona Enter cuando termines (ctrl+d para finalizar):"
        EC2_SSH_KEY=$(cat)
        
        # Actualizar todos
        echo ""
        echo "Actualizando secrets en GitHub..."
        gh secret set AWS_ACCESS_KEY_ID --body "$AWS_ACCESS_KEY_ID" --repo "$REPO"
        gh secret set AWS_SECRET_ACCESS_KEY --body "$AWS_SECRET_ACCESS_KEY" --repo "$REPO"
        gh secret set AWS_SESSION_TOKEN --body "$AWS_SESSION_TOKEN" --repo "$REPO"
        gh secret set DOCKERHUB_USERNAME --body "$DOCKERHUB_USERNAME" --repo "$REPO"
        gh secret set DOCKERHUB_TOKEN --body "$DOCKERHUB_TOKEN" --repo "$REPO"
        gh secret set EC2_HOST --body "$EC2_HOST" --repo "$REPO"
        gh secret set EC2_USER --body "$EC2_USER" --repo "$REPO"
        gh secret set EC2_SSH_KEY --body "$EC2_SSH_KEY" --repo "$REPO"
        
        echo ""
        echo -e "${GREEN}✓ Todos los secrets actualizados exitosamente${NC}"
        ;;
        
    3)
        echo ""
        echo -e "${YELLOW}Actualizando credenciales de Docker Hub...${NC}"
        echo ""
        
        read -p "DOCKERHUB_USERNAME = " DOCKERHUB_USERNAME
        read -sp "DOCKERHUB_TOKEN = " DOCKERHUB_TOKEN
        echo ""
        
        echo ""
        echo "Actualizando secrets en GitHub..."
        gh secret set DOCKERHUB_USERNAME --body "$DOCKERHUB_USERNAME" --repo "$REPO"
        gh secret set DOCKERHUB_TOKEN --body "$DOCKERHUB_TOKEN" --repo "$REPO"
        
        echo ""
        echo -e "${GREEN}✓ Credenciales de Docker Hub actualizadas${NC}"
        ;;
        
    4)
        echo ""
        echo -e "${YELLOW}Actualizando credenciales de EC2...${NC}"
        echo ""
        
        read -p "EC2_HOST (IP pública) = " EC2_HOST
        read -p "EC2_USER (default: ec2-user) = " EC2_USER
        EC2_USER=${EC2_USER:-ec2-user}
        
        echo ""
        echo "Para EC2_SSH_KEY, pega el contenido COMPLETO de tu archivo .pem"
        echo "Presiona Enter cuando termines (ctrl+d para finalizar):"
        EC2_SSH_KEY=$(cat)
        
        echo ""
        echo "Actualizando secrets en GitHub..."
        gh secret set EC2_HOST --body "$EC2_HOST" --repo "$REPO"
        gh secret set EC2_USER --body "$EC2_USER" --repo "$REPO"
        gh secret set EC2_SSH_KEY --body "$EC2_SSH_KEY" --repo "$REPO"
        
        echo ""
        echo -e "${GREEN}✓ Credenciales de EC2 actualizadas${NC}"
        ;;
        
    *)
        echo -e "${RED}Opción inválida${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${GREEN}Proceso completado exitosamente${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""
echo "Próximos pasos:"
echo "  1. Verifica los secrets en: https://github.com/$REPO/settings/secrets/actions"
echo "  2. Haz un push para ejecutar el pipeline"
echo "  3. Monitorea la ejecución en: https://github.com/$REPO/actions"
echo ""
