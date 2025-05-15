#!/usr/bin/env python3
"""
Script para traduzir arquivos Markdown do inglês para o português
usando a biblioteca deep-translator, preservando formatações e elementos especiais.
"""

import os
import re
import sys
import time
import argparse
from pathlib import Path
from deep_translator import GoogleTranslator

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
    
    # Padrões a preservar (ampliado)
    if preserve_patterns is None:
        preserve_patterns = [
            # Emojis e ícones
            r':[a-zA-Z0-9_-]+:',
            # Links Markdown
            r'\[([^\]]+)\]\(([^)]+)\)',
            # Código inline
            r'`[^`]+`',
            # Tags HTML
            r'<[^>]+>',
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
            # Material MkDocs específico
            r':[a-zA-Z0-9_-]+:',
            r'\{[^}]+\}',
            # URLs
            r'https?://[^\s)]+',
            # Admonições MkDocs
            r'^!!!.*$',
        ]
    
    # Salvar partes que não devem ser traduzidas
    for pattern in preserve_patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            placeholder = f"<<<PLACEHOLDER_{counter}>>>"
            placeholders[placeholder] = match.group(0)
            text = text.replace(match.group(0), placeholder)
            counter += 1
    
    # Se depois de remover todos os padrões não tiver conteúdo para traduzir
    if not ''.join(text.split()).strip():
        # Restaurar as partes preservadas
        for placeholder, original in placeholders.items():
            text = text.replace(placeholder, original)
        return text
    
    # Dividir em pedaços menores para traduzir (limitação da API)
    max_chars = 4000
    chunks = []
    
    if len(text) <= max_chars:
        chunks = [text]
    else:
        start = 0
        while start < len(text):
            end = start + max_chars
            if end >= len(text):
                chunks.append(text[start:])
                break
            
            # Tentar terminar em um ponto final, vírgula ou quebra de linha
            for i in range(min(end, len(text)-1), start, -1):
                if text[i] in '.,:;\n':
                    end = i + 1
                    break
            
            chunks.append(text[start:end])
            start = end
    
    # Traduzir cada pedaço
    translated_chunks = []
    for chunk in chunks:
        try:
            if chunk.strip():
                translated = translator.translate(chunk)
                translated_chunks.append(translated)
            else:
                translated_chunks.append(chunk)
            time.sleep(0.5)  # Pequena pausa para evitar sobrecarga da API
        except Exception as e:
            print(f"Erro ao traduzir: {e}")
            translated_chunks.append(chunk)
    
    # Juntar os pedaços traduzidos
    translated_text = ''.join(translated_chunks)
    
    # Restaurar as partes preservadas
    for placeholder, original in placeholders.items():
        translated_text = translated_text.replace(placeholder, original)
    
    return translated_text

def process_file_content(content):
    """
    Processa o conteúdo do arquivo, extraindo partes que não devem ser traduzidas.
    
    Args:
        content: Conteúdo do arquivo
        
    Returns:
        Tupla com os padrões extraídos e o conteúdo processado
    """
    # Inicializar dicionários vazios para todos os padrões
    patterns = {
        'frontmatter': None,
        'code_blocks': {},
        'html_comments': {},
        'html_tags': {},
        'admonitions': {}
    }
    
    # Extrair frontmatter
    frontmatter_pattern = r'^---\n([\s\S]*?)\n---'
    frontmatter_match = re.match(frontmatter_pattern, content)
    
    if frontmatter_match:
        patterns['frontmatter'] = frontmatter_match.group(0)
        content = content.replace(patterns['frontmatter'], "<<<FRONTMATTER>>>")
    
    # Extrair blocos de código
    code_block_pattern = r'```[a-zA-Z0-9_]*\n[\s\S]*?```'
    
    for i, match in enumerate(re.finditer(code_block_pattern, content)):
        placeholder = f"<<<CODEBLOCK_{i}>>>"
        patterns['code_blocks'][placeholder] = match.group(0)
        content = content.replace(match.group(0), placeholder)
    
    # Extrair comentários HTML
    comment_pattern = r'<!--[\s\S]*?-->'
    
    for i, match in enumerate(re.finditer(comment_pattern, content)):
        placeholder = f"<<<COMMENT_{i}>>>"
        patterns['html_comments'][placeholder] = match.group(0)
        content = content.replace(match.group(0), placeholder)
    
    # Extrair HTML tags complexos
    html_pattern = r'<(?!br|hr|img)[a-z]+[^>]*>[\s\S]*?</[a-z]+>'
    
    for i, match in enumerate(re.finditer(html_pattern, content, re.IGNORECASE)):
        placeholder = f"<<<HTML_{i}>>>"
        patterns['html_tags'][placeholder] = match.group(0)
        content = content.replace(match.group(0), placeholder)
        
    # Extrair admonitions do MkDocs Material
    admonition_start_pattern = r'^!!! [^\n]+$'
    
    lines = content.split('\n')
    in_admonition = False
    current_admonition = []
    admonition_count = 0
    processed_lines = []
    
    for line in lines:
        if re.match(admonition_start_pattern, line) and not in_admonition:
            in_admonition = True
            current_admonition = [line]
        elif in_admonition:
            if line.startswith('    ') or not line.strip():
                current_admonition.append(line)
            else:
                # Admonition terminou
                admonition_text = '\n'.join(current_admonition)
                placeholder = f"<<<ADMONITION_{admonition_count}>>>"
                patterns['admonitions'][placeholder] = admonition_text
                processed_lines.append(placeholder)
                admonition_count += 1
                in_admonition = False
                processed_lines.append(line)
        else:
            processed_lines.append(line)
    
    # Verificar se terminou com um admonition
    if in_admonition:
        admonition_text = '\n'.join(current_admonition)
        placeholder = f"<<<ADMONITION_{admonition_count}>>>"
        patterns['admonitions'][placeholder] = admonition_text
        processed_lines.append(placeholder)
    
    # Reconstruir o conteúdo processado
    content = '\n'.join(processed_lines)
    
    return patterns, content

def restore_patterns(content, patterns):
    """
    Restaura os padrões extraídos no conteúdo traduzido.
    
    Args:
        content: Conteúdo traduzido
        patterns: Dicionário de padrões extraídos
        
    Returns:
        Conteúdo com os padrões restaurados
    """
    # Restaurar frontmatter
    if patterns['frontmatter']:
        content = content.replace("<<<FRONTMATTER>>>", patterns['frontmatter'])
    
    # Restaurar blocos de código
    for placeholder, code_block in patterns['code_blocks'].items():
        content = content.replace(placeholder, code_block)
    
    # Restaurar comentários HTML
    for placeholder, comment in patterns['html_comments'].items():
        content = content.replace(placeholder, comment)
    
    # Restaurar HTML tags
    for placeholder, tag in patterns['html_tags'].items():
        content = content.replace(placeholder, tag)
    
    # Restaurar admonitions
    for placeholder, admonition in patterns['admonitions'].items():
        content = content.replace(placeholder, admonition)
    
    return content

def translate_markdown_file(input_file, output_file, translator, delay=1.0):
    """
    Traduz um arquivo Markdown preservando sua estrutura.
    
    Args:
        input_file: Caminho do arquivo de entrada
        output_file: Caminho do arquivo de saída
        translator: Instância do tradutor
        delay: Tempo de espera entre traduções (segundos)
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extrair e processar partes especiais
        patterns, processed_content = process_file_content(content)
        
        # Dividir por linhas para tradução
        lines = processed_content.split('\n')
        translated_lines = []
        
        # Traduzir linha por linha
        for i, line in enumerate(lines):
            # Verificar se é uma linha especial que contém um placeholder
            contains_placeholder = False
            for pattern_dict in patterns.values():
                if isinstance(pattern_dict, dict):  # Verifica se é um dicionário
                    for placeholder in pattern_dict.keys():
                        if placeholder in line:
                            contains_placeholder = True
                            break
                if contains_placeholder:
                    break
            
            if contains_placeholder:
                translated_lines.append(line)
                continue
            
            # Verificar se é um cabeçalho Markdown
            header_match = re.match(r'^(#+)\s+(.+)$', line)
            if header_match:
                prefix = header_match.group(1)
                header_text = header_match.group(2)
                translated_header = safe_translate(header_text, translator)
                translated_lines.append(f"{prefix} {translated_header}")
            # Linha normal
            else:
                translated_line = safe_translate(line, translator)
                translated_lines.append(translated_line)
            
            # Adicionar uma pequena pausa a cada 5 linhas
            if i % 5 == 0 and i > 0:
                time.sleep(delay)
        
        # Juntar as linhas traduzidas
        translated_content = '\n'.join(translated_lines)
        
        # Restaurar as partes extraídas
        final_content = restore_patterns(translated_content, patterns)
        
        # Criar diretório de saída se necessário
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(final_content)
        
        print(f"✅ Arquivo traduzido: {output_file}")
        
    except Exception as e:
        print(f"❌ Erro ao traduzir {input_file}: {str(e)}")

def translate_directory(input_dir, output_dir, translator, delay=1.0):
    """
    Traduz todos os arquivos Markdown em um diretório e subdiretórios.
    
    Args:
        input_dir: Caminho do diretório de entrada
        output_dir: Caminho do diretório de saída
        translator: Instância do tradutor
        delay: Tempo de espera entre traduções (segundos)
    """
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.md'):
                # Construir caminhos de entrada e saída
                rel_path = os.path.relpath(root, input_dir)
                input_file = os.path.join(root, file)
                
                if rel_path == '.':
                    output_file = os.path.join(output_dir, file)
                else:
                    output_file = os.path.join(output_dir, rel_path, file)
                
                # Traduzir o arquivo
                print(f"Traduzindo {os.path.join(rel_path, file)}...")
                translate_markdown_file(input_file, output_file, translator, delay)
                
                # Pausa entre arquivos
                time.sleep(delay * 2)

def main():
    parser = argparse.ArgumentParser(description='Traduz arquivos Markdown do inglês para o português.')
    parser.add_argument('input', help='Arquivo ou diretório de entrada para traduzir')
    parser.add_argument('output', help='Arquivo ou diretório de saída para salvar a tradução')
    parser.add_argument('--delay', type=float, default=1.0, help='Tempo de espera (segundos) entre traduções')
    
    args = parser.parse_args()
    
    # Criar o tradutor
    translator = GoogleTranslator(source='en', target='pt')
    
    # Verificar se é um arquivo ou diretório
    if os.path.isdir(args.input):
        translate_directory(args.input, args.output, translator, args.delay)
    else:
        translate_markdown_file(args.input, args.output, translator, args.delay)
    
    print("Tradução concluída!")

if __name__ == '__main__':
    main()
