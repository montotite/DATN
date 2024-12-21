
const device_ls = document.getElementById("device_ls");

function load_device(data) {
    data.data.forEach(element => {
        console.log(element.name)
        const item = document.createElement('div');
        item.className = "col-lg-3"
        item.innerHTML = `
        <div class="card">
            <div class="card-body">
                <h5 class="card-title">${element.name}</h5>
                <p class="card-text">
                
                
                
                </p>
                <a href="#" class="card-link">Chi tiết</a>
            </div>
        </div>    
        `
        device_ls.appendChild(item)
    });
}

fetch('http://103.176.251.60:32770/api/device?page_size=10&page=0')
    .then(response => response.json())
    .then(data => load_device(data))
    .catch(error => console.error('Error:', error));