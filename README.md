# CHAATGPT — Character Studio MCP

Servidor MCP para gerar especificações e scripts procedurais de personagens 3D no Blender.

## Ferramentas MCP

- `create_character_brief`: cria um briefing de produção para humanos, criaturas e monstros.
- `generate_blender_character_script`: entrega um script Python executável no Blender que cria um personagem humanoide básico e um armature.
- `list_character_presets`: lista presets iniciais.

## Executar o gerador no Blender

1. Abra o Blender 3.6 ou superior.
2. Vá para o espaço de trabalho **Scripting**.
3. Crie um texto novo.
4. Use a ferramenta MCP `generate_blender_character_script` para obter o script.
5. Cole o código Python no editor de texto do Blender e clique em **Run Script**.

O primeiro gerador é um blockout procedural: malha montada a partir de volumes, materiais simples e rig humanoide básico. Não é um personagem hiper-realista final. Para produção, ainda será necessário esculpir/refinar a topologia, fazer UVs, texturas, roupa, cabelo, pesos e testes de deformação.

## Publicar no Cloudflare Workers

O Worker configurado em `wrangler.jsonc` chama-se `character-studio-mcp`, igual ao Worker existente.

Para conectar o repositório existente:
1. Abra Cloudflare Dashboard > **Workers & Pages**.
2. Selecione o Worker **character-studio-mcp**.
3. Abra **Settings > Builds** e escolha **Connect**.
4. Conecte a conta GitHub e selecione `pauloharidade88-stack/CHAATGPT), branch `main`.
5. Deixe o diretório raiz como `/`, sem build command obrigatório e deploy command `npx wrangler deploy`.
6. Salve. Um novo commit na branch `main` inicia o build e deploy automaticamente.

Depois de publicar, o endpoint MCP será:
`https://character-studio-mcp.paulinhoderick2019.workers.dev/mcp`

A rota raiz apenas mostra a mensagem de status.

## Desenvolvimento local

```bash
npm install
npm run dev
```

O endpoint local MCP fica em `http://localhost:8787/mcp`.

## Próximas etapas

- Melhorar anatomia, mãos, pés, rosto e silhuetas.
- Criar rigs quadrúpedes e rigs personalizados para monstros.
- Adicionar geração de roupas, acessórios, UVs e materiais.
- Adicionar exportação e validação de FBX/GLB.
- Proteger o endpoint com autenticação antes de expor ferramentas sensíveis.
