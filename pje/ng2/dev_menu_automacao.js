window.websocket = null;  // Variável global para armazenar o WebSocket ativo
function abrirWebSocketEEnviarMensagem(mensagem) {
    debugger
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
        };

        // Configura o evento onerror para tratar erros
        websocket.onerror = function(error) {
            console.error("Erro WebSocket: " + error.message);
        };

        // Configura o evento onclose para quando a conexão for fechada
        websocket.onclose = function() {
            console.log("Conexão WebSocket fechada");
        };
    } else {
        // Caso já exista uma conexão aberta, apenas envia a mensagem
        console.log('Usando WebSocket existente...');
        websocket.send(JSON.stringify(mensagem));
        console.log(`Mensagem enviada: ${mensagem}`);
    }
}
console.log('dev.seam: script do menu de automação foi devidamente carregado')