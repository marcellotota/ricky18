
async function loadAlbum() {

    const gallery = document.getElementById("gallery");

    try {

        const response = await fetch("photos.json");

        if (!response.ok) {
            throw new Error("Impossibile caricare photos.json");
        }

        const photos = await response.json();

        photos.forEach(photo => {

            const item = document.createElement("div");

            item.className = `photo ${photo.layout}`;

            const img = document.createElement("img");

            img.src = photo.src;
            img.alt = photo.date || photo.filename;
            img.loading = "lazy";

            item.appendChild(img);

            const caption = document.createElement("div");

            caption.className = "photo-caption";

            caption.textContent = photo.date
                ? new Date(
                    photo.date + "T12:00:00"
                  ).toLocaleDateString("it-IT", {
                    day: "numeric",
                    month: "long",
                    year: "numeric"
                  })
                : photo.filename;

            item.appendChild(caption);

            gallery.appendChild(item);

        });

    } catch (error) {

        console.error(error);

        gallery.textContent =
            "Errore durante il caricamento delle fotografie.";

    }

}

loadAlbum();
