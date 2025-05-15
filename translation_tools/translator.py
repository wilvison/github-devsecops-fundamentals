#!/usr/bin/env python3
import os
import json
import shutil
import subprocess
import sys
import tempfile

# Lista de traduções em português do Brasil
TRANSLATIONS = {
    "Search": "Pesquisar",
    "Previous": "Anterior",
    "Next": "Próximo",
    "Home": "Início",
    "Language": "Idioma",
    "Edit on": "Editar no",
    "Edit this page": "Editar esta página",
    "Last update": "Última atualização",
    "Table of Contents": "Índice",
    "No results found": "Nenhum resultado encontrado",
    "Search Results": "Resultados da pesquisa",
    "Project information": "Informações do projeto",
    "Repository": "Repositório",
    "Version": "Versão",
    "Build Date": "Data de compilação",
    "Copyright": "Direitos autorais",
    "Last updated on": "Última atualização em",
    "Please activate JavaScript to enable the search functionality.": "Por favor, ative o JavaScript para habilitar a funcionalidade de pesquisa."
}

def create_translations():
    """
    Cria ou atualiza os arquivos de tradução para o MkDocs Material
    """
    print("Criando traduções em português brasileiro para o MkDocs Material...")
    
    try:
        # Encontrar o caminho do pacote material
        result = subprocess.run(
            ["python3", "-c", "from importlib.metadata import distribution; print(distribution('mkdocs-material').locate_file('material'))"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode != 0:
            print("Erro ao localizar o pacote mkdocs-material. Verificando instalação alternativa...")
            result = subprocess.run(
                ["find", "/usr", "-path", "*/site-packages/material", "-type", "d"],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.stdout.strip():
                material_path = result.stdout.strip().split("\n")[0]
            else:
                print("Não foi possível encontrar o pacote material. O MkDocs Material está instalado?")
                return False
        else:
            material_path = result.stdout.strip()
        
        print(f"Pacote material encontrado em: {material_path}")
        
        # Verificar se existe a pasta translations
        translations_path = os.path.join(material_path, "translations")
        if not os.path.exists(translations_path):
            print(f"Pasta de traduções não encontrada em {translations_path}")
            return False
        
        # Verificar se já existe a pasta pt_BR com o arquivo de tradução
        pt_br_file = os.path.join(translations_path, "pt_BR.json")
        
        # Se não existir, criar
        if os.path.exists(pt_br_file):
            print(f"Arquivo de tradução existe em {pt_br_file}. Vamos adicionar as traduções faltantes.")
            try:
                with open(pt_br_file, 'r', encoding='utf-8') as f:
                    existing_translations = json.load(f)
                
                # Adicionar traduções faltantes
                was_updated = False
                for key, value in TRANSLATIONS.items():
                    if key not in existing_translations:
                        existing_translations[key] = value
                        was_updated = True
                
                if was_updated:
                    # Criar um arquivo temporário primeiro
                    with tempfile.NamedTemporaryFile('w', encoding='utf-8', delete=False) as tmp:
                        json.dump(existing_translations, tmp, ensure_ascii=False, indent=2)
                        tmp_path = tmp.name
                    
                    # Copiar para o destino final usando sudo se necessário
                    try:
                        shutil.copy2(tmp_path, pt_br_file)
                        print(f"Adicionadas novas traduções ao arquivo {pt_br_file}")
                    except PermissionError:
                        print(f"Erro de permissão ao atualizar {pt_br_file}")
                        print(f"Tente executar: sudo cp {tmp_path} {pt_br_file}")
                        return False
                    finally:
                        os.unlink(tmp_path)
                else:
                    print("Nenhuma nova tradução para adicionar.")
            except (json.JSONDecodeError, PermissionError) as e:
                print(f"Erro ao ler ou atualizar o arquivo de tradução: {e}")
                return False
        else:
            print(f"Criando novo arquivo de tradução em {pt_br_file}")
            try:
                # Criar um arquivo temporário primeiro
                with tempfile.NamedTemporaryFile('w', encoding='utf-8', delete=False) as tmp:
                    json.dump(TRANSLATIONS, tmp, ensure_ascii=False, indent=2)
                    tmp_path = tmp.name
                
                # Copiar para o destino final usando sudo se necessário
                try:
                    shutil.copy2(tmp_path, pt_br_file)
                    print(f"Arquivo de tradução criado em {pt_br_file}")
                except PermissionError:
                    print(f"Erro de permissão ao criar {pt_br_file}")
                    print(f"Tente executar: sudo cp {tmp_path} {pt_br_file}")
                    return False
                finally:
                    os.unlink(tmp_path)
            except Exception as e:
                print(f"Erro ao criar arquivo de tradução: {e}")
                return False
        
        # Atualizar o arquivo mkdocs.yml se necessário
        update_mkdocs_config()
        
        print("\nTraduções em português brasileiro configuradas com sucesso!")
        print("Agora você pode executar 'mkdocs build' ou 'mkdocs serve' novamente")
        print("para ver o site com as traduções em português.")
        return True
    except Exception as e:
        print(f"Ocorreu um erro: {str(e)}")
        return False

def update_mkdocs_config():
    """
    Atualiza o arquivo mkdocs.yml para remover configurações de locale_dirs
    que não são suportadas e garantir que o locale está configurado corretamente.
    """
    mkdocs_yml_path = "/workspaces/devsecops-fundamentals/mkdocs.yml"
    
    try:
        with open(mkdocs_yml_path, "r", encoding="utf-8") as f:
            config_content = f.read()
        
        # Remover a linha locale_dirs que não é suportada
        if "locale_dirs:" in config_content:
            # Dividir o conteúdo em linhas para manipulação linha por linha
            lines = config_content.split("\n")
            filtered_lines = []
            
            for line in lines:
                if "locale_dirs:" not in line:
                    filtered_lines.append(line)
            
            updated_content = "\n".join(filtered_lines)
            
            # Escrever o arquivo atualizado
            with open(mkdocs_yml_path, "w", encoding="utf-8") as f:
                f.write(updated_content)
                
            print(f"Arquivo {mkdocs_yml_path} atualizado: removida configuração locale_dirs")
    except Exception as e:
        print(f"Erro ao atualizar o arquivo mkdocs.yml: {e}")

if __name__ == "__main__":
    success = create_translations()
    if not success:
        sys.exit(1)
