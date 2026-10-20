Grupo ENG — Landing Page

Landing page institucional do Grupo ENG, grupo com três frentes de atuação: Construção Civil, Locação de Máquinas Pesadas e Transportes e Logística.

Feita com HTML5, CSS3 e JavaScript puro, sem frameworks e sem etapa de build. Para ver o site, basta abrir o index.html.

Estrutura do projeto
grupo-eng/
├── index.html      # Estrutura e conteúdo da página
├── style.css       # Estilos (variáveis no :root, mobile-first)
├── script.js       # Menu mobile, WhatsApp, galeria, formulário e animações
├── README.md
└── img/            # Logo e fotos (veja a lista abaixo)
Como rodar
Abra a pasta no VS Code.
Instale a extensão Live Server (opcional, mas recomendada).
Clique com o botão direito em index.html e escolha Open with Live Server.

Também funciona abrindo o index.html direto no navegador.

Imagens necessárias (pasta img/)
Arquivo	Uso
grupo-eng-dark.png	Logo para fundo escuro (header e rodapé)
hero.jpg	Foto principal do topo da página
obra-01.jpg, obra-02.jpg	Obras prontas e equipe em campo
maquina-01.jpg, maquina-02.jpg, maquina-03.jpg	Maquinário em operação
caminhao-01.jpg, caminhao-02.jpg	Frota de caminhões

Enquanto uma foto não existir, o site usa uma imagem de exemplo (atributo data-fallback), então a página não fica com imagem quebrada.

Personalização
WhatsApp

Edite a constante no topo do script.js:

js
const WHATSAPP_NUMBER = "5500000000000"; // DDI + DDD + número, só dígitos

Todos os botões se atualizam. A mensagem de cada botão fica no atributo data-wa="..." do index.html.

Cores, fontes e arredondamentos

Edite as variáveis no :root, no topo do style.css:

css
:root {
  --orange: #f36b16;
  --ink: #09090b;
  --paper: #f6f5f2;
  --font-title: "Barlow Condensed", sans-serif;
  --r-xl: 2.5rem;
}
Galeria

Para adicionar uma foto, copie um bloco <figure class="g" data-cat="..."> no index.html e altere src, alt, data-cat (obras, frota ou maquinas) e a legenda. Para destacar uma foto em telas maiores, use as classes g-big, g-wide ou g-tall.

Contato, mapa e redes sociais

No index.html, procure pelos comentários ENDEREÇO, TELEFONE, E-MAIL, SOCIAL e MAPA. Para o mapa, use o Google Maps em Compartilhar > Incorporar um mapa e cole o src do iframe.

Checklist antes de publicar
 Número de WhatsApp real no script.js
 Telefone, e-mail, endereço e redes sociais atualizados
 Mapa apontando para o endereço correto
 Logo e fotos reais na pasta img/
 Números da seção de diferenciais confirmados com o cliente
 Depoimentos de exemplo trocados por depoimentos reais (com autorização)
 Teste em celular, tablet e desktop
Recursos
Layout responsivo, mobile-first
Menu mobile com acessibilidade (aria-expanded, tecla Esc)
Galeria com filtro por categoria e ampliação de fotos (<dialog> nativo)
Formulário que envia o pedido pelo WhatsApp, sem servidor
Animações de entrada com IntersectionObserver, respeitando prefers-reduced-motion
Publicação

Por ser um site estático, pode ser hospedado gratuitamente em Netlify, Vercel ou GitHub Pages: basta enviar a pasta do projeto.

© Grupo ENG. Todos os direitos reservados.
