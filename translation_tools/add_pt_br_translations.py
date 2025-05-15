#!/usr/bin/env python3
import os
import shutil
import subprocess
import sys

def add_pt_br_translations():
    """
    Script para adicionar traduções em português brasileiro ao MkDocs no diretório local do projeto.
    """
    print("Adicionando traduções em português brasileiro ao MkDocs...")
    
    # Criar diretório local para traduções
    try:
        # Diretório do projeto
        project_dir = "/workspaces/devsecops-fundamentals"
        
        # Criar estrutura de diretórios para as traduções locais
        locale_dir = os.path.join(project_dir, "locales")
        pt_br_path = os.path.join(locale_dir, "pt_BR", "LC_MESSAGES")
        os.makedirs(pt_br_path, exist_ok=True)
        
        print(f"Diretório de traduções criado em: {pt_br_path}")
        
        # Criar arquivo .po básico com traduções para português brasileiro
        po_file_content = '''
msgid ""
msgstr ""
"Project-Id-Version: mkdocs\\n"
"Report-Msgid-Bugs-To: \\n"
"POT-Creation-Date: 2023-01-01 00:00+0000\\n"
"PO-Revision-Date: 2023-01-01 00:00+0000\\n"
"Last-Translator: Copilot <copilot@github.com>\\n"
"Language-Team: Portuguese\\n"
"Language: pt_BR\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"

msgid "Search"
msgstr "Pesquisar"

msgid "Previous"
msgstr "Anterior"

msgid "Next"
msgstr "Próximo"

msgid "Edit on"
msgstr "Editar em"

msgid "Home"
msgstr "Início"

msgid "Table of Contents"
msgstr "Índice"

msgid "Project information"
msgstr "Informações do projeto"

msgid "Repository"
msgstr "Repositório"

msgid "Version"
msgstr "Versão"

msgid "Build Date"
msgstr "Data de compilação"

msgid "Copyright"
msgstr "Direitos autorais"

msgid "Language"
msgstr "Idioma"

msgid "Last updated on"
msgstr "Última atualização em"

msgid "Search Results"
msgstr "Resultados da pesquisa"

msgid "No results found"
msgstr "Nenhum resultado encontrado"

msgid "Please activate JavaScript to enable the search functionality."
msgstr "Por favor, ative o JavaScript para habilitar a funcionalidade de pesquisa."
'''
        
        # Salvar o arquivo .po
        po_file_path = os.path.join(pt_br_path, "messages.po")
        with open(po_file_path, "w", encoding="utf-8") as f:
            f.write(po_file_content)
        
        # Compilar o arquivo .po para .mo
        try:
            subprocess.run(
                ["msgfmt", po_file_path, "-o", os.path.join(pt_br_path, "messages.mo")],
                check=True
            )
            print(f"Arquivo de tradução compilado com sucesso: {os.path.join(pt_br_path, 'messages.mo')}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Erro ao compilar o arquivo de tradução.")
            print("Verificando se msgfmt está instalado...")
            print("Você pode precisar instalar o pacote 'gettext' usando:")
            print("  apt-get update && apt-get install -y gettext")
            return False
        
        # Atualizar o arquivo mkdocs.yml para usar as traduções locais
        update_mkdocs_config(project_dir, locale_dir)
        
        print("Traduções em português adicionadas com sucesso!")
        print("\nAgora você pode executar 'mkdocs build' ou 'mkdocs serve' novamente")
        print("para ver o site com as traduções em português.")
        return True
        
    except Exception as e:
        print(f"Ocorreu um erro: {str(e)}")
        return False

def update_mkdocs_config(project_dir, locale_dir):
    """
    Atualiza o arquivo mkdocs.yml para incluir o caminho para as traduções locais.
    """
    mkdocs_yml_path = os.path.join(project_dir, "mkdocs.yml")
    
    # Ler o arquivo de configuração atual
    with open(mkdocs_yml_path, "r", encoding="utf-8") as f:
        config_content = f.read()
    
    # Verificar se já existe uma entrada para locale_dir
    if "locale_dir:" not in config_content:
        # Encontrar a seção de tema
        theme_index = config_content.find("theme:")
        if theme_index != -1:
            # Encontrar o fim da seção do tema procurando pela próxima seção
            next_section = config_content.find("\n\n", theme_index)
            if next_section == -1:  # Não encontrou o fim da seção
                next_section = len(config_content)
            
            # Caminho relativo ao diretório do projeto
            relative_path = os.path.relpath(locale_dir, project_dir)
            
            # Inserir a configuração de locale_dir na seção do tema
            locale_config = f"\n  locale_dirs: [\"{relative_path}\"]"
            updated_content = (
                config_content[:next_section] + 
                locale_config + 
                config_content[next_section:]
            )
            
            # Escrever o arquivo atualizado
            with open(mkdocs_yml_path, "w", encoding="utf-8") as f:
                f.write(updated_content)
                
            print(f"Arquivo {mkdocs_yml_path} atualizado com sucesso!")
        else:
            print("Não foi possível encontrar a seção 'theme' no arquivo mkdocs.yml")
    else:
        print("A configuração locale_dir já existe no arquivo mkdocs.yml")

if __name__ == "__main__":
    success = add_pt_br_translations()
    if not success:
        sys.exit(1)