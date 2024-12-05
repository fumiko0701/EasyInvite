// Função que será chamada quando o botão for clicado
document.getElementById('searchBtn').addEventListener('click', function() {
    var searchIdValue = document.getElementById("searchId").value.trim();
    if (searchIdValue) {
        // Redireciona para a página de visualização com o ID inserido
        window.location.href = "/view/" + searchIdValue;
    } else {
        alert("Por favor, insira um ID válido.");
    }
});
