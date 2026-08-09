console.log("=================================");
console.log("AI VOICE TRANSLATOR - SCRIPT V4");
console.log("=================================");


const uploadBtn = document.getElementById("uploadbtn");
const fileInput = document.getElementById("audiofile");

const statusText = document.getElementById("status");

const transcript = document.getElementById("transcript");
const translation = document.getElementById("translation");
const pronunciation = document.getElementById("pronunciation");

const fileName = document.getElementById("fileName");
const dropArea = document.getElementById("dropArea");


// Prevent multiple requests
let isProcessing = false;


// ======================================================
// FILE SELECTION
// ======================================================

fileInput.addEventListener("change", function () {

    if (fileInput.files.length > 0) {

        const file = fileInput.files[0];

        console.log("File selected:", file.name);

        fileName.textContent =
            "Selected: " + file.name;
    }
});


// ======================================================
// DRAG AND DROP
// ======================================================

["dragenter", "dragover"].forEach(eventName => {

    dropArea.addEventListener(eventName, function (event) {

        event.preventDefault();

        dropArea.style.borderColor = "#245778";
        dropArea.style.background = "#eef7f9";
    });
});


["dragleave", "drop"].forEach(eventName => {

    dropArea.addEventListener(eventName, function (event) {

        event.preventDefault();

        dropArea.style.borderColor = "";
        dropArea.style.background = "";
    });
});


dropArea.addEventListener("drop", function (event) {

    const files = event.dataTransfer.files;

    if (files.length > 0) {

        fileInput.files = files;

        console.log(
            "Dropped file:",
            files[0].name
        );

        fileName.textContent =
            "Selected: " + files[0].name;
    }
});


// ======================================================
// TRANSLATE AUDIO
// ======================================================

uploadBtn.addEventListener("click", async function () {

    console.log("Translate button clicked");


    // --------------------------------------------------
    // PREVENT MULTIPLE REQUESTS
    // --------------------------------------------------

    if (isProcessing) {

        console.log(
            "Request already running. Ignoring click."
        );

        return;
    }


    // --------------------------------------------------
    // CHECK FILE
    // --------------------------------------------------

    if (fileInput.files.length === 0) {

        statusText.textContent =
            "Please choose an audio file first.";

        statusText.style.color = "#b14d4d";

        return;
    }


    // --------------------------------------------------
    // LOCK REQUEST
    // --------------------------------------------------

    isProcessing = true;

    uploadBtn.disabled = true;

    uploadBtn.textContent =
        "PROCESSING...";


    const file = fileInput.files[0];

    console.log("Processing:", file.name);


    // --------------------------------------------------
    // CREATE FORM DATA
    // --------------------------------------------------

    const formData = new FormData();

    formData.append("audio", file);


    // --------------------------------------------------
    // SHOW PROCESSING STATE
    // --------------------------------------------------

    statusText.textContent =
        "Processing audio...";

    statusText.style.color =
        "#3f96ad";


    transcript.textContent =
        "Transcribing your speech...";


    translation.textContent =
        "Waiting for translation...";


    pronunciation.textContent =
        "Waiting for pronunciation...";


    try {

        // ==================================================
        // SEND REQUEST TO FLASK
        // ==================================================

        console.log(
            "Sending POST /transcribe"
        );


        const response = await fetch(
            "http://127.0.0.1:5000/transcribe",
            {
                method: "POST",
                body: formData
            }
        );


        console.log(
            "Server response status:",
            response.status
        );


        // ==================================================
        // READ RESPONSE
        // ==================================================

        const data = await response.json();


        console.log(
            "Server returned:",
            data
        );


        // ==================================================
        // SERVER ERROR
        // ==================================================

        if (!response.ok) {

            throw new Error(
                data.message ||
                "Server returned an error."
            );
        }


        // ==================================================
        // DISPLAY TRANSCRIPT
        // ==================================================

        transcript.textContent =
            data.transcript ||
            "No transcript available.";


        // ==================================================
        // DISPLAY TRANSLATION
        // ==================================================

        translation.textContent =
            data.translation ||
            "No translation available.";


        // ==================================================
        // DISPLAY PRONUNCIATION
        // ==================================================

        pronunciation.textContent =
            data.pronunciation ||
            "No pronunciation available.";


        // ==================================================
        // SUCCESS
        // ==================================================

        statusText.textContent =
            "Translation completed successfully.";

        statusText.style.color =
            "#2d7f59";


        console.log(
            "RESULTS SUCCESSFULLY DISPLAYED"
        );

    }


    catch (error) {

        console.error(
            "FRONTEND ERROR:",
            error
        );


        statusText.textContent =
            "Something went wrong while processing the audio.";

        statusText.style.color =
            "#b14d4d";


        transcript.textContent =
            "Unable to retrieve transcript.";


        translation.textContent =
            "Unable to retrieve translation.";


        pronunciation.textContent =
            "Unable to retrieve pronunciation.";
    }


    finally {

        // ==================================================
        // UNLOCK BUTTON
        // ==================================================

        uploadBtn.disabled = false;

        uploadBtn.textContent =
            "TRANSLATE AUDIO";

        isProcessing = false;

        console.log(
            "Request finished."
        );
    }

});