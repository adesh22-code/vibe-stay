let homestays = [];


async function loadHomestays() {

    const table = document.getElementById("homestayTable");
    const total = document.getElementById("totalHomestays");
    const message = document.getElementById("message");

    try {

        const response = await fetch("/api/homestays");

        if (!response.ok) {
            throw new Error("Failed to load homestays");
        }

        homestays = await response.json();

        total.textContent = `${homestays.length} homestays`;

        table.innerHTML = "";

        homestays.forEach((homestay, index) => {

            const row = document.createElement("tr");

            row.innerHTML = `
                <td>${homestay.id ?? ""}</td>

                <td>
                    ${
                        homestay.image
                            ? `<img src="${homestay.image}" alt="">`
                            : "No image"
                    }
                </td>

                <td>${homestay.name ?? ""}</td>

                <td>${homestay.location ?? ""}</td>

                <td>₹${homestay.price ?? ""}</td>

                <td>
                    <button
                        type="button"
                        class="edit-button"
                        onclick="editHomestay(${index})">
                        Edit
                    </button>
                </td>
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


function editHomestay(index) {

    const homestay = homestays[index];

    if (!homestay) {
        return;
    }


    document.getElementById("editId").value =
        homestay.id ?? "";

    document.getElementById("name").value =
        homestay.name ?? "";

    document.getElementById("location").value =
        homestay.location ?? "";

    document.getElementById("price").value =
        homestay.price ?? "";

    document.getElementById("scenery").value =
        homestay.scenery ?? "";

    document.getElementById("amenities").value =
        homestay.amenities ?? "";

    document.getElementById("description").value =
        homestay.description ?? "";

    document.getElementById("phone").value =
        homestay.phone ?? "";

    document.getElementById("whatsapp").value =
        homestay.whatsapp ?? "";

    document.getElementById("facebook").value =
        homestay.facebook ?? "";

    document.getElementById("website").value =
        homestay.website ?? "";

    document.getElementById("youtube").value =
        homestay.youtube ?? "";

    document.getElementById("instagram").value =
        homestay.instagram ?? "";

    document.getElementById("googleMap").value =
        homestay.googleMap ?? "";

    document.getElementById("gallery").value =
        homestay.gallery ?? "";

    document.getElementById("image").value =
        homestay.image ?? "";


    document.getElementById("listSection").style.display =
        "none";

    document.getElementById("editSection").style.display =
        "block";

    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
}


function cancelEdit() {

    document.getElementById("editSection").style.display =
        "none";

    document.getElementById("listSection").style.display =
        "block";
}


document.getElementById("cancelEdit").addEventListener(
    "click",
    cancelEdit
);


document.getElementById("cancelEdit2").addEventListener(
    "click",
    cancelEdit
);


document.getElementById("saveButton").addEventListener(
    "click",
    function () {

        alert(
            "Save is not connected yet. We will connect it to GitHub in the next step."
        );

    }
);


loadHomestays();
