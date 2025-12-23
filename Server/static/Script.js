

console.log("dlwkefwjebfwef")

// code from https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
document.addEventListener("DOMContentLoaded", function () {
    const response_box = document.getElementBy("response");
    const form = document.getElementById('loginform');

    if (form) {
        form.addEventListener('submit', async function (e) {
            e.preventDefault();

            // 1. Correctly initialize FormData
            const formData = new FormData(e.target);
            
            // 2. Convert FormData to a plain JavaScript object for JSON serialization
            const data = Object.fromEntries(formData.entries());

            try {
                const response = await fetch("/handle_login", {
                    method: "POST",
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    // 4. Stringify the object to send as JSON
                    body: JSON.stringify(data)
                });

                if (response.ok) {
                    window.location.href = "{{ url_for('Browse') }}";
                } else if (response.status === 401) {
                    const response_json = await response.json();
                    
                    response_box.innerText = response_json.message;
                    response_box.className = "alert alert-danger";
                } else {
                    // Handle other errors
                    console.error('Unexpected status:', response.status);
                }
            } catch (error) {
                console.error("Fetch error:", error);
            }
        });
    }
});

// code from https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
document.addEventListener("DOMContentLoaded", function () {
    const response_box = document.getElementBy("response");
    const form = document.getElementById('registerform');

    if (form) {
        form.addEventListener('submit', async function (e) {
            e.preventDefault();

            // 1. Correctly initialize FormData
            const formData = new FormData(e.target);
            
            // 2. Convert FormData to a plain JavaScript object for JSON serialization
            const data = Object.fromEntries(formData.entries());

            try {
                const response = await fetch("/handle_register", {
                    method: "POST",
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    // 4. Stringify the object to send as JSON
                    body: JSON.stringify(data)
                });

                if (response.ok) {
                    window.location.href = "{{ url_for('Browse') }}";
                } else if (response.status === 401) {
                    const response_json = await response.json();
                    
                    response_box.innerText = response_json.message;
                    response_box.className = "alert alert-danger";
                } else {
                    // Handle other errors
                    console.error('Unexpected status:', response.status);
                }
            } catch (error) {
                console.error("Fetch error:", error);
            }
        });
    }
});


