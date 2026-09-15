
const form = document.getElementById("registrationForm");
const errorMessage = document.getElementById("errorMessage");

const sellerFields = document.getElementById("sellerFields");
const storeName = document.getElementById("storeName");
const storeDescription = document.getElementById("storeDescription");

// img left side  
document.addEventListener("DOMContentLoaded", function () {

    const readerRole = document.getElementById("readerRole");
    const sellerRole = document.getElementById("sellerRole");
    const roleImage = document.getElementById("roleImage");

    const readerImage =
        "https://rukmini1.flixcart.com/image/1500/1500/xif0q/sticker/p/x/k/large-book-store-library-reader-leader-1-33-1458wfykyne-original-imah9rvswzfgsxsy.jpeg?q=70";

    const sellerImage =
        "https://images.unsplash.com/photo-1532012197267-da84d127e765?q=80&w=387&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D";

    function changeRoleImage() {

        if (sellerRole.checked) {
            roleImage.style.backgroundImage = `url("${sellerImage}")`;
        } else {
            roleImage.style.backgroundImage = `url("${readerImage}")`;
        }

    }

    readerRole.addEventListener("change", changeRoleImage);
    sellerRole.addEventListener("change", changeRoleImage);

    changeRoleImage();
});


// =====================================
// ROLE CHANGE
// =====================================

const roleInputs = document.querySelectorAll('input[name="role"]');

roleInputs.forEach(function (radio) {

    radio.addEventListener("change", function () {

        if (this.value === "seller") {

            sellerFields.classList.remove("hidden");

            storeName.required = true;
            storeDescription.required = true;

        } else {

            sellerFields.classList.add("hidden");

            storeName.required = false;
            storeDescription.required = false;

            storeName.value = "";
            storeDescription.value = "";
        }
        clearError();
    });
});

// =====================================
// FORM SUBMIT VALIDATION
// =====================================

fdocument.addEventListener("DOMContentLoaded", function () {

    // =====================================
    // GET ELEMENTS
    // =====================================

    const form = document.getElementById("registrationForm");
    const errorMessage = document.getElementById("errorMessage");

    const readerRole = document.getElementById("readerRole");
    const sellerRole = document.getElementById("sellerRole");

    const sellerFields = document.getElementById("sellerFields");
    const storeName = document.getElementById("storeName");
    const storeDescription = document.getElementById("storeDescription");

    const roleImage = document.getElementById("roleImage");

    const fullName = document.getElementById("fullName");
    const username = document.getElementById("username");
    const email = document.getElementById("email");
    const phone = document.getElementById("phone");
    const location = document.getElementById("location");

    const password = document.getElementById("password");
    const confirmPassword = document.getElementById("confirmPassword");

    const profilePhoto = document.querySelector(
        'input[name="profile_photo"]'
    );

    const terms = document.getElementById("terms");


    // =====================================
    // CHECK FORM EXISTS
    // =====================================

    if (!form) {
        console.error("Registration form not found.");
        return;
    }


    // =====================================
    // ROLE IMAGES
    // =====================================

    const readerImage =
        "https://rukmini1.flixcart.com/image/1500/1500/xif0q/sticker/p/x/k/large-book-store-library-reader-leader-1-33-1458wfykyne-original-imah9rvswzfgsxsy.jpeg?q=70";

    const sellerImage =
        "https://images.unsplash.com/photo-1532012197267-da84d127e765?q=80&w=387&auto=format&fit=crop";


    function changeRoleImage() {

        if (!roleImage) {
            return;
        }

        if (sellerRole && sellerRole.checked) {

            roleImage.style.backgroundImage =
                `url("${sellerImage}")`;

        } else {

            roleImage.style.backgroundImage =
                `url("${readerImage}")`;
        }
    }


    // =====================================
    // SELLER FIELDS
    // =====================================

    function updateSellerFields() {

        if (!sellerFields) {
            return;
        }

        if (sellerRole && sellerRole.checked) {

            sellerFields.classList.remove("hidden");

            if (storeName) {
                storeName.required = true;
            }

            if (storeDescription) {
                storeDescription.required = true;
            }

        } else {

            sellerFields.classList.add("hidden");

            if (storeName) {
                storeName.required = false;
            }

            if (storeDescription) {
                storeDescription.required = false;
            }
        }

        clearError();
    }


    // =====================================
    // ROLE CHANGE
    // =====================================

    if (readerRole) {
        readerRole.addEventListener("change", function () {
            updateSellerFields();
            changeRoleImage();
        });
    }

    if (sellerRole) {
        sellerRole.addEventListener("change", function () {
            updateSellerFields();
            changeRoleImage();
        });
    }


    // Initial state
    updateSellerFields();
    changeRoleImage();


    // =====================================
    // FORM SUBMIT
    // =====================================

    form.addEventListener("submit", function (event) {

        // Stop Django form submission temporarily
        event.preventDefault();

        clearError();


        // =====================================
        // SELECTED ROLE
        // =====================================

        const selectedRole = document.querySelector(
            'input[name="role"]:checked'
        );

        if (!selectedRole) {

            showError("Please select a role.");
            return;
        }


        // =====================================
        // FULL NAME
        // =====================================

        const fullNameValue = fullName.value.trim();

        if (fullNameValue === "") {

            showError("Please enter your Full Name.");
            fullName.focus();
            return;
        }

        if (fullNameValue.length < 2) {

            showError(
                "Full Name must contain at least 2 characters."
            );

            fullName.focus();
            return;
        }

        const namePattern = /^[A-Za-z ]+$/;

        if (!namePattern.test(fullNameValue)) {

            showError(
                "Full Name can contain only letters and spaces."
            );

            fullName.focus();
            return;
        }


        // =====================================
        // USERNAME
        // =====================================

        const usernameValue = username.value.trim();

        if (usernameValue === "") {

            showError("Please enter Username.");
            username.focus();
            return;
        }

        if (usernameValue.length < 4) {

            showError(
                "Username must contain at least 4 characters."
            );

            username.focus();
            return;
        }

        const usernamePattern = /^[A-Za-z0-9_]+$/;

        if (!usernamePattern.test(usernameValue)) {

            showError(
                "Username can contain only letters, numbers and underscore."
            );

            username.focus();
            return;
        }


        // =====================================
        // EMAIL
        // =====================================

        const emailValue = email.value.trim();

        if (emailValue === "") {

            showError("Please enter Email Address.");
            email.focus();
            return;
        }

        const emailPattern =
            /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (!emailPattern.test(emailValue)) {

            showError(
                "Please enter a valid Email Address."
            );

            email.focus();
            return;
        }


        // =====================================
        // PHONE
        // =====================================

        const phoneValue = phone.value.trim();

        if (phoneValue === "") {

            showError("Please enter Phone Number.");
            phone.focus();
            return;
        }

        const phonePattern = /^[0-9]{10}$/;

        if (!phonePattern.test(phoneValue)) {

            showError(
                "Phone Number must contain exactly 10 digits."
            );

            phone.focus();
            return;
        }


        // =====================================
        // LOCATION
        // =====================================

        const locationValue = location.value.trim();

        if (locationValue === "") {

            showError(
                "Please enter City / Location."
            );

            location.focus();
            return;
        }

        if (locationValue.length < 2) {

            showError(
                "Please enter a valid Location."
            );

            location.focus();
            return;
        }


        // =====================================
        // PROFILE PHOTO
        // =====================================

        if (!profilePhoto || profilePhoto.files.length === 0) {

            showError(
                "Please upload your Profile Photo."
            );

            return;
        }


        // =====================================
        // SELLER VALIDATION
        // =====================================

        if (selectedRole.value === "seller") {

            const storeNameValue =
                storeName.value.trim();

            const storeDescriptionValue =
                storeDescription.value.trim();


            // Store Name

            if (storeNameValue === "") {

                showError(
                    "Please enter Store Name."
                );

                storeName.focus();
                return;
            }


            if (storeNameValue.length < 2) {

                showError(
                    "Store Name must contain at least 2 characters."
                );

                storeName.focus();
                return;
            }


            // Store Description

            if (storeDescriptionValue === "") {

                showError(
                    "Please enter Store Description."
                );

                storeDescription.focus();
                return;
            }


            if (storeDescriptionValue.length < 10) {

                showError(
                    "Store Description must contain at least 10 characters."
                );

                storeDescription.focus();
                return;
            }
        }


        // =====================================
        // PASSWORD
        // =====================================

        const passwordValue = password.value;

        if (passwordValue === "") {

            showError(
                "Please enter Password."
            );

            password.focus();
            return;
        }


        if (passwordValue.length < 8) {

            showError(
                "Password must contain at least 8 characters."
            );

            password.focus();
            return;
        }


        // Uppercase

        if (!/[A-Z]/.test(passwordValue)) {

            showError(
                "Password must contain at least one uppercase letter."
            );

            password.focus();
            return;
        }


        // Lowercase

        if (!/[a-z]/.test(passwordValue)) {

            showError(
                "Password must contain at least one lowercase letter."
            );

            password.focus();
            return;
        }


        // Number

        if (!/[0-9]/.test(passwordValue)) {

            showError(
                "Password must contain at least one number."
            );

            password.focus();
            return;
        }


        // Special Character

        if (!/[!@#$%^&*]/.test(passwordValue)) {

            showError(
                "Password must contain at least one special character."
            );

            password.focus();
            return;
        }


        // =====================================
        // CONFIRM PASSWORD
        // =====================================

        const confirmPasswordValue =
            confirmPassword.value;


        if (confirmPasswordValue === "") {

            showError(
                "Please confirm your Password."
            );

            confirmPassword.focus();
            return;
        }


        if (passwordValue !== confirmPasswordValue) {

            showError(
                "Password and Confirm Password do not match."
            );

            confirmPassword.focus();
            return;
        }


        // =====================================
        // TERMS
        // =====================================

        if (!terms || !terms.checked) {

            showError(
                "Please accept the Terms of Service and Privacy Policy."
            );

            if (terms) {
                terms.focus();
            }

            return;
        }


        // =====================================
        // EVERYTHING VALID
        // =====================================

        clearError();

        // Allow Django to submit the form
        form.submit();

    });


    // =====================================
    // SHOW ERROR
    // =====================================

    function showError(message) {

        if (!errorMessage) {
            alert(message);
            return;
        }

        errorMessage.textContent = message;

        errorMessage.classList.remove("hidden");

        errorMessage.scrollIntoView({
            behavior: "smooth",
            block: "center"
        });
    }


    // =====================================
    // CLEAR ERROR
    // =====================================

    function clearError() {

        if (!errorMessage) {
            return;
        }

        errorMessage.textContent = "";

        errorMessage.classList.add("hidden");
    }

});
