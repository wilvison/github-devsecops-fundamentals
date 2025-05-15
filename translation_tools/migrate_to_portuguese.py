#!/usr/bin/env python3
import os
import shutil
import sys

def migrate_pt_content():
    """
    Script para migrar o conteúdo em português para a pasta docs padrão do MkDocs.
    """
    print("Migrando documentação em português para a pasta docs padrão...")
    
    # Verificar se as pastas existem
    if not os.path.exists('docs-pt'):
        print("Erro: A pasta docs-pt não existe!")
        return False
    
    # Fazer backup da pasta docs original se ela existir
    if os.path.exists('docs'):
        print("Fazendo backup da pasta docs original...")
        try:
            if os.path.exists('docs.bak'):
                shutil.rmtree('docs.bak')
            shutil.move('docs', 'docs.bak')
            print("Backup criado em docs.bak")
        except Exception as e:
            print(f"Erro ao criar backup: {e}")
            return False
    
    # Criar pasta docs se não existir
    if not os.path.exists('docs'):
        os.makedirs('docs')
    
    # Copiar conteúdo de docs-pt para docs
    try:
        print("Copiando conteúdo de docs-pt para docs...")
        for item in os.listdir('docs-pt'):
            source = os.path.join('docs-pt', item)
            destination = os.path.join('docs', item)
            
            if os.path.isdir(source):
                shutil.copytree(source, destination, dirs_exist_ok=True)
            else:
                shutil.copy2(source, destination)
        
        print("Conteúdo copiado com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao copiar conteúdo: {e}")
        return False

if __name__ == "__main__":
    success = migrate_pt_content()
    if success:
        print("\nA migração foi concluída com sucesso!")
        print("Agora você pode construir seu site usando apenas: mkdocs build")
        print("\nApós verificar que tudo está funcionando corretamente, você pode remover")
        print("a pasta docs-pt e o arquivo mkdocs.pt.yml se desejar.")
    else:
        print("\nA migração falhou. Por favor, verifique os erros acima.")
        sys.exit(1)