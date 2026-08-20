async function loadHomestays() {
    const table = document.getElementById("homestayTable");
    const total = document.getElementById("totalHomestays");
    const message = document.getElementById("message");

    try {
        const response = await fetch("/api/homestays");

        if (!response.ok) {
            throw new Error("Failed to load homestays");
        }

        const homestays = await response.json();

        total.textContent = `${homestays.length} homestays`;

        table.innerHTML = "";

        homestays.forEach((homestay) => {
            const row = document.createElement("tr");

            row.innerHTML = `
                <td>${homestay.id ?? ""}</td>

                <td>
                    ${
                        homestay.image
                            ? `<img src="${homestay.image}" alt="${homestay.name ?? ""}">`
                            : "No image"
                    }
                </td>

                <td>${homestay.name ?? ""}</td>

                <td>${homestay.location ?? ""}</td>

                <td>₹${homestay.price ?? ""}</td>

                <td>${homestay.phone ?? ""}</td>
            `;

            table.appendChild(row);
        });

    } catch (error) {
        console.error(error);

        total.textContent = "";

        message.textContent =
            "Unable to load homestays.";

        table.innerHTML = `
            <tr>
                <td colspan="6">
                    Error loading data.
                </td>
            </tr>
        `;
    }
}


loadHomestays();
