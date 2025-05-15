#!/usr/bin/env python3
"""
Script para traduzir arquivos Markdown do inglês para o português
usando a biblioteca googletrans, preservando formatações e elementos especiais.
"""

import os
import re
import sys
import time
import argparse
from pathlib import Path
from googletrans import Translator

def safe_translate(text, translator, preserve_patterns=None):
    """
    Traduz o texto preservando padrões específicos.
    
    Args:
        text: Texto para traduzir
        translator: Instância do tradutor
        preserve_patterns: Lista de padrões regex para preservar
        
    Returns:
        Texto traduzido com os padrões preservados
    """
    if not text.strip():
        return text
    
    # Identificadores para substituição temporária
    placeholders = {}
    counter = 0
    
    # Padrões a preservar
    if preserve_patterns is None:
        preserve_patterns = [
            # Links Markdown
            r'\[([^\]]+)\]\(([^)]+)\)',
            # Código inline
            r'`[^`]+`',
            # Tags HTML
            r'<[^>]+>',
            # Emojis e ícones
            r':[a-zA-Z0-9_-]+:',
            # Referências de imagens Markdown
            r'!\[[^\]]*\]\([^)]+\)',
            # Formatação Markdown
            r'\*\*[^*]+\*\*',  # negrito
            r'\*[^*]+\*',      # itálico
            r'~~[^~]+~~',      # tachado
            # Marcadores e listas
            r'^(\s*[-*+]\s+)',
            r'^(\s*\d+\.\s+)',
            # Variáveis e macros
            r'\{\{[^}]+\}\}',
            r'\{%[^%]+%\}',
            # Admonições MkDocs Material
            r'!!!.*',
            # Comandos e variáveis específicas
            r'\$[a-zA-Z0-9_]+',
            # URLs
            r'https?://[^\s)]+',
            # Figuras Markdown
            r'<figure.*?</figure>',
            # Estilos inline
            r'\{[^}]*\}',
            # Elementos de classes e sintaxe especial do MkDocs
            r'\{[.=].*?\}',
            # Comentários HTML
            r'<!--.*?-->',
        ]
    
    # Salvar partes que não devem ser traduzidas
    for pattern in preserve_patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            placeholder = f"__PLACEHOLDER_{counter}__"
            placeholders[placeholder] = match.group(0)
            text = text.replace(match.group(0), placeholder)
            counter += 1
    
    # Traduzir o texto
    try:
        if text.strip():
            translated = translator.translate(text, src='en', dest='pt')
            translated_text = translated.text
        else:
            translated_text = text
    except Exception as e:
        print(f"Erro ao traduzir: {e}")
        return text
    
    # Restaurar as partes preservadas
    for placeholder, original in placeholders.items():
        translated_text = translated_text.replace(placeholder, original)
    
    return translated_text

def extract_codeblocks(content):
    """
    Extrai blocos de código do conteúdo e os substitui por placeholders.
    
    Args:
        content: Conteúdo Markdown
        
    Returns:
        Tupla com o conteúdo modificado e dicionário de blocos de código
    """
    # Regex para blocos de código
    code_block_pattern = r'```[a-zA-Z0-9_]*\n[\s\S]*?```'
    
    # Encontrar todos os blocos de código
    code_blocks = {}
    counter = 0
    
    for match in re.finditer(code_block_pattern, content):
        placeholder = f"__CODEBLOCK_{counter}__"
        code_blocks[placeholder] = match.group(0)
        content = content.replace(match.group(0), placeholder)
        counter += 1
    
    return content, code_blocks

def extract_frontmatter(content):
    """
    Extrai o frontmatter YAML (se existir) e o substitui por placeholder.
    
    Args:
        content: Conteúdo Markdown
        
    Returns:
        Tupla com o conteúdo modificado e o frontmatter
    """
    frontmatter_pattern = r'^---\n([\s\S]*?)\n---'
    match = re.match(frontmatter_pattern, content)
    
    if match:
        frontmatter = match.group(0)
        content = content.replace(frontmatter, "__FRONTMATTER__")
        return content, frontmatter
    
    return content, None

def extract_html_comments(content):
    """
    Extrai comentários HTML e os substitui por placeholders.
    
    Args:
        content: Conteúdo Markdown
        
    Returns:
        Tupla com o conteúdo modificado e dicionário de comentários
    """
    comment_pattern = r'<!--[\s\S]*?-->'
    
    # Encontrar todos os comentários HTML
    comments = {}
    counter = 0
    
    for match in re.finditer(comment_pattern, content):
        placeholder = f"__COMMENT_{counter}__"
        comments[placeholder] = match.group(0)
        content = content.replace(match.group(0), placeholder)
        counter += 1
    
    return content, comments

def extract_admonitions(content):
    """
    Extrai admonitions do MkDocs Material e os substitui por placeholders.
    
    Args:
        content: Conteúdo Markdown
        
    Returns:
        Tupla com o conteúdo modificado e dicionário de admonitions
    """
    # Regex para admonitions do MkDocs Material
    admonition_pattern = r'!!!.*?\n(?:\s{4}.*?\n)+(?:\n|$)'
    
    # Encontrar todos os admonitions
    admonitions = {}
    counter = 0
    
    for match in re.finditer(admonition_pattern, content, re.MULTILINE):
        placeholder = f"__ADMONITION_{counter}__"
        admonitions[placeholder] = match.group(0)
        content = content.replace(match.group(0), placeholder)
        counter += 1
    
    return content, admonitions

def translate_markdown_file(input_file, output_file, translator, delay=1):
    """
    Traduz um arquivo Markdown preservando sua estrutura.
    
    Args:
        input_file: Caminho do arquivo de entrada
        output_file: Caminho do arquivo de saída
        translator: Instância do tradutor
        delay: Tempo de espera entre traduções para evitar bloqueio (em segundos)
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extrair frontmatter
        content, frontmatter = extract_frontmatter(content)
        
        # Extrair blocos de código
        content, code_blocks = extract_codeblocks(content)
        
        # Extrair comentários HTML
        content, html_comments = extract_html_comments(content)
        
        # Extrair admonitions
        content, admonitions = extract_admonitions(content)
        
        # Dividir o conteúdo em linhas
        lines = content.split('\n')
        
        translated_lines = []
        for i, line in enumerate(lines):
            # Pular linhas vazias
            if not line.strip():
                translated_lines.append(line)
                continue
                
            # Verificar se é um cabeçalho
            header_match = re.match(r'^(#+)\s+(.+)$', line)
            if header_match:
                prefix = header_match.group(1)
                text = header_match.group(2)
                translated_text = safe_translate(text, translator)
                translated_lines.append(f"{prefix} {translated_text}")
            # Verificar se é uma linha especial (HTML, frontmatter etc.)
            elif any(placeholder in line for placeholder in list(code_blocks.keys()) + 
                   list(html_comments.keys()) + list(admonitions.keys())):
                # Não traduzir se contém placeholder
                translated_lines.append(line)
            else:
                # Traduzir a linha normalmente
                translated_line = safe_translate(line, translator)
                translated_lines.append(translated_line)
            
            # Adicionar um pequeno atraso para evitar bloqueio da API
            if i % 5 == 0 and i > 0:
                time.sleep(delay)
        
        # Juntar as linhas traduzidas
        translated_content = '\n'.join(translated_lines)
        
        # Restaurar os blocos de código
        for placeholder, code_block in code_blocks.items():
            translated_content = translated_content.replace(placeholder, code_block)
        
        # Restaurar os comentários HTML
        for placeholder, comment in html_comments.items():
            translated_content = translated_content.replace(placeholder, comment)
            
        # Restaurar os admonitions
        for placeholder, admonition in admonitions.items():
            translated_content = translated_content.replace(placeholder, admonition)
        
        # Restaurar o frontmatter
        if frontmatter:
            translated_content = translated_content.replace("__FRONTMATTER__", frontmatter)
        
        # Criar diretório de saída se não existir
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Salvar o conteúdo traduzido
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(translated_content)
            
        print(f"✅ Arquivo traduzido: {output_file}")
    
    except Exception as e:
        print(f"❌ Erro ao traduzir {input_file}: {e}")

def translate_directory(input_dir, output_dir, delay=1):
    """
    Traduz todos os arquivos Markdown em um diretório e seus subdiretórios.
    
    Args:
        input_dir: Diretório de entrada
        output_dir: Diretório de saída
        delay: Tempo de espera entre traduções para evitar bloqueio (em segundos)
    """
    translator = Translator()
    
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.md'):
                # Construir caminhos
                input_file = os.path.join(root, file)
                rel_path = os.path.relpath(input_file, input_dir)
                output_file = os.path.join(output_dir, rel_path)
                
                print(f"Traduzindo {rel_path}...")
                translate_markdown_file(input_file, output_file, translator, delay)
                # Pausa entre arquivos para evitar sobrecarga
                time.sleep(delay * 2)

def main():
    parser = argparse.ArgumentParser(description='Traduz arquivos Markdown preservando elementos especiais.')
    parser.add_argument('input', help='Arquivo ou diretório de entrada')
    parser.add_argument('output', help='Arquivo ou diretório de saída')
    parser.add_argument('--delay', type=float, default=1.0, help='Tempo de espera entre traduções (em segundos)')
    parser.add_argument('--retry', action='store_true', help='Tentar novamente arquivos já traduzidos')
    
    args = parser.parse_args()
    
    # Verificar se entrada existe
    if not os.path.exists(args.input):
        print(f"Erro: {args.input} não existe.")
        return 1
    
    # Se for um diretório
    if os.path.isdir(args.input):
        translate_directory(args.input, args.output, args.delay)
    else:
        # Criar diretório de saída
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        translator = Translator()
        translate_markdown_file(args.input, args.output, translator, args.delay)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
