// chamada quando o botão for clicado
document.getElementById('searchBtn').addEventListener('click', function() {
    var searchIdValue = document.getElementById("searchId").value.trim();
    if (searchIdValue) {
        //redireciona para a view do ID
        window.location.href = "/view/" + searchIdValue;
    } else {
        alert("Por favor, insira um ID válido.");
    }
});
