console.log("Frontend Loaded Successfully");

const uploadbtn = document.getElementById("uploadbtn");

uploadbtn.addEventListener("click", async () => {

    console.log("Upload button clicked");

    const fileInput = document.getElementById("audiofile");

    if (fileInput.files.length === 0) {
        alert("Please choose a file");
        return;
    }

    console.log("File selected:", fileInput.files[0].name);

    const formData = new FormData();

    formData.append(
        "audio",
        fileInput.files[0]
    );

    try {

        console.log("Sending request...");

        const response = await fetch(
            "http://127.0.0.1:5000/transcribe",
            {
                method: "POST",
                body: formData
            }
        );

        console.log("Response status:", response.status);

        const data = await response.json();

        console.log("Received data:", data);

        document.getElementById("status").innerText =
            "Transcription completed";

        document.getElementById("transcript").innerText =
            data.transcript;

    } catch (error) {

        console.error("ERROR:", error);

    }
});
console.log("SCRIPT VERSION 2");