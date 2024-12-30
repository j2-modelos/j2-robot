window.websocket = null;  // Variável global para armazenar o WebSocket ativo
function abrirWebSocketEEnviarMensagem(mensagem) {
    debugger
    const liElement = event.target.closest('li');
    if (liElement.classList.contains('disabled')) return

    const porta = window.J2_ROBO_WEBSOCKET_PORTA
    if (!websocket || websocket.readyState === WebSocket.CLOSED) {
        // Se não houver uma conexão ativa, ou ela foi fechada, crie uma nova
        console.log('Abrindo nova conexão WebSocket...');
        websocket = new WebSocket(`ws://localhost:${porta}`);

        // Configura o evento onopen para quando a conexão for bem-sucedida
        websocket.onopen = function() {
            console.log("Conexão WebSocket estabelecida");

            // Envia a mensagem recebida pela função
            websocket.send(JSON.stringify(mensagem));
            console.log(`Mensagem enviada: ${mensagem}`);
        };

        // Configura o evento onmessage para receber mensagens do servidor WebSocket
        websocket.onmessage = function(event) {
            console.log("Mensagem recebida do servidor: " + event.data);

            console.log("Mensagem recebida do servidor:", event.data);

            // Você pode adicionar lógica adicional aqui, por exemplo:
            const resposta = JSON.parse(event.data);
            console.log("Dados da resposta", resposta);

            switch(resposta.acao){
                case 'estado-lista-de-automacoes':
                    estadoAutomacoes(resposta.estado)
                    break;
            }
        };

        // Configura o evento onerror para tratar erros
        websocket.onerror = function(error) {
            console.error("Erro WebSocket: " + error.message);
        };

        // Configura o evento onclose para quando a conexão for fechada
        websocket.onclose = function() {
            console.log("Conexão WebSocket fechada. Tentando reconectar...");
            tentarReconectar("Mensagem após reconexão");
        };
    } else {
        // Caso já exista uma conexão aberta, apenas envia a mensagem
        console.log('Usando WebSocket existente...');
        websocket.send(JSON.stringify(mensagem));
        console.log(`Mensagem enviada: ${mensagem}`);
    }
}
function tentarReconectar(mensagem) {
    setTimeout(() => {
        console.log('Tentando reconectar...');
        abrirWebSocketEEnviarMensagem(mensagem);
    }, 3000);  // Tenta reconectar após 3 segundos
}
function estadoAutomacoes(estado) {
    // Seleciona todos os elementos <li> dentro de elementos com atributo [j2-robot]
    const listaItens = document.querySelectorAll('[j2-robot] li');

    // Itera sobre todos os itens e adiciona a classe 'disabled'
    listaItens.forEach(function(item) {
        item.classList[estado ? 'remove' : 'add']('disabled');
    });
}
console.log('dev.seam: script do menu de automação foi devidamente carregado')