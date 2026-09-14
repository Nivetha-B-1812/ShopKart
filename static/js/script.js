document.addEventListener("DOMContentLoaded", function () {

    const slides = document.querySelectorAll(".banner-slide");
    const dots = document.querySelectorAll(".banner-dot");
    const nextButton = document.querySelector(".banner-next");
    const prevButton = document.querySelector(".banner-prev");

    let currentSlide = 0;
    let autoSlide;

    function showSlide(index) {

        slides.forEach(function (slide) {
            slide.classList.remove("active");
        });

        dots.forEach(function (dot) {
            dot.classList.remove("active");
        });

        currentSlide = (index + slides.length) % slides.length;

        slides[currentSlide].classList.add("active");

        if (dots[currentSlide]) {
            dots[currentSlide].classList.add("active");
        }
    }

    function nextSlide() {
        showSlide(currentSlide + 1);
    }

    function previousSlide() {
        showSlide(currentSlide - 1);
    }

    function startAutoSlide() {
        clearInterval(autoSlide);

        autoSlide = setInterval(function () {
            nextSlide();
        }, 3000);
    }

    if (nextButton) {
        nextButton.addEventListener("click", function () {
            nextSlide();
            startAutoSlide();
        });
    }

    if (prevButton) {
        prevButton.addEventListener("click", function () {
            previousSlide();
            startAutoSlide();
        });
    }

    dots.forEach(function (dot, index) {
        dot.addEventListener("click", function () {
            showSlide(index);
            startAutoSlide();
        });
    });

    if (slides.length > 0) {
        showSlide(0);
        startAutoSlide();
    }

});

/* =========================================================
   PRODUCT QUANTITY
   ========================================================= */

const quantityMinus = document.querySelector(".quantity-minus");
const quantityPlus = document.querySelector(".quantity-plus");
const quantityValue = document.querySelector("#quantityValue");

if (quantityMinus && quantityPlus && quantityValue) {

    let quantity = 1;

    quantityMinus.addEventListener("click", function () {

        if (quantity > 1) {
            quantity--;
            quantityValue.textContent = quantity;
        }

    });

    quantityPlus.addEventListener("click", function () {

        if (quantity < 10) {
            quantity++;
            quantityValue.textContent = quantity;
        }

    });

}

/* =========================================================
   PRODUCT PAGE - ADD TO CART
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    const addToCartBtn = document.getElementById("addToCartBtn");

    if (!addToCartBtn) {
        return;
    }

    addToCartBtn.addEventListener("click", function () {

        const productId = this.getAttribute("data-product-id");

        const quantityElement =
            document.getElementById("quantityValue");

        const quantity = quantityElement
            ? parseInt(quantityElement.textContent) || 1
            : 1;

        fetch("/add-to-cart/" + productId, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                quantity: quantity
            })
        })

        .then(function (response) {
            return response.json();
        })

        .then(function (data) {

            if (data.success) {

                const cartCount =
                    document.querySelector(".cart-count");

                if (cartCount) {
                    cartCount.textContent = data.cart_count;
                }

                window.location.href = "/cart";

            } else {

                console.log("Add to cart failed");

            }

        })

        .catch(function (error) {

            console.error(
                "Add to cart error:",
                error
            );

        });

    });

});

/* =========================================================
   CART TOTAL CALCULATION
   ========================================================= */

function updateCartTotals() {

    const cartItems = document.querySelectorAll(".cart-item");

    let subtotal = 0;
    let totalItems = 0;

    cartItems.forEach(function (item) {

        const priceElement = item.querySelector(".cart-price");
        const quantityElement = item.querySelector(".cart-quantity span");

        if (!priceElement || !quantityElement) {
            return;
        }

        const price = parseFloat(
            priceElement.textContent
                .replace("₹", "")
                .replace(/,/g, "")
        );

        const quantity = parseInt(quantityElement.textContent);

        subtotal += price * quantity;
        totalItems += quantity;
    });

    const subtotalElement = document.querySelector("#cartSubtotal");
    const totalElement = document.querySelector("#cartTotal");

    if (subtotalElement) {
        subtotalElement.textContent =
            "₹" + subtotal.toLocaleString("en-IN", {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
    }

    const discount = subtotal * 0.10;
const finalTotal = subtotal - discount;

const discountElement = document.querySelector("#cartDiscount");

if (discountElement) {
    discountElement.textContent =
        "-₹" + discount.toLocaleString("en-IN", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
}

if (totalElement) {
    totalElement.textContent =
        "₹" + finalTotal.toLocaleString("en-IN", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
}

    const itemsElement = document.querySelector(
        ".cart-summary .summary-row:first-of-type span:last-child"
    );

    if (itemsElement) {
        itemsElement.textContent = totalItems;
    }
}


document.addEventListener("DOMContentLoaded", function () {
    updateCartTotals();
});

/* =========================================================
   CART QUANTITY + REMOVE
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    const cartItems = document.querySelectorAll(".cart-item");

    cartItems.forEach(function (item) {

        const minusButton = item.querySelector(".cart-minus");
        const plusButton = item.querySelector(".cart-plus");
        const removeButton = item.querySelector(".remove-cart-btn");
        const quantityElement = item.querySelector(".cart-quantity span");

        const productId = minusButton
            ? minusButton.dataset.productId
            : null;


        /* =========================
           UPDATE QUANTITY
           ========================= */

        function updateQuantity(quantity) {

            if (quantity < 1) {
                quantity = 1;
            }

            if (quantity > 10) {
                quantity = 10;
            }

            fetch(`/update-cart/${productId}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    quantity: quantity
                })
            })

            .then(response => response.json())

            .then(data => {

                if (data.success) {

                    quantityElement.textContent = quantity;

                    updateCartTotals();

                }

            })

            .catch(error => {
                console.error("Cart update error:", error);
            });
        }


        /* =========================
           MINUS
           ========================= */

        if (minusButton) {

            minusButton.addEventListener("click", function () {

                let quantity =
                    parseInt(quantityElement.textContent);

                if (quantity > 1) {
                    quantity--;
                    updateQuantity(quantity);
                }

            });
        }


        /* =========================
           PLUS
           ========================= */

        if (plusButton) {

            plusButton.addEventListener("click", function () {

                let quantity =
                    parseInt(quantityElement.textContent);

                if (quantity < 10) {
                    quantity++;
                    updateQuantity(quantity);
                }

            });
        }


        /* =========================
           REMOVE
           ========================= */

        if (removeButton) {

            removeButton.addEventListener("click", function () {

                fetch(`/remove-from-cart/${productId}`, {
                    method: "POST"
                })

                .then(response => response.json())

                .then(data => {

                    if (data.success) {

                        item.remove();

                        updateCartTotals();

                        if (document.querySelectorAll(".cart-item").length === 0) {
                            location.reload();
                        }

                    }

                })

                .catch(error => {
                    console.error("Remove cart error:", error);
                });

            });
        }

    });

});

/* =========================================================
   CATEGORY PAGE - ADD TO CART
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    const categoryButtons =
        document.querySelectorAll(".category-add-cart");

    categoryButtons.forEach(function (button) {

        button.addEventListener("click", function () {

            const productId =
                this.getAttribute("data-product-id");

            fetch("/add-to-cart/" + productId, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    quantity: 1
                })
            })

            .then(function (response) {
                return response.json();
            })

            .then(function (data) {

                if (data.success) {

                    button.textContent = "Added to Cart";

                    const cartCount =
                        document.querySelector(".cart-count");

                    if (cartCount) {
                        cartCount.textContent =
                            data.cart_count;
                    }

                    setTimeout(function () {
                        button.textContent = "Add to Cart";
                    }, 1500);
                }

            })

            .catch(function (error) {
                console.error(
                    "Category Add to Cart Error:",
                    error
                );
            });

        });

    });

});
/* =========================================================
   SEARCH RESULTS - ADD TO CART
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    const searchButtons =
        document.querySelectorAll(".search-add-cart");

    searchButtons.forEach(function (button) {

        button.addEventListener("click", function () {

            const productId =
                this.getAttribute("data-product-id");

            fetch("/add-to-cart/" + productId, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    quantity: 1
                })
            })

            .then(function (response) {
                return response.json();
            })

            .then(function (data) {

                if (data.success) {

                    button.textContent = "Added to Cart";

                    const cartCount =
                        document.querySelector(".cart-count");

                    if (cartCount) {
                        cartCount.textContent =
                            data.cart_count;
                    }

                    setTimeout(function () {
                        button.textContent = "Add to Cart";
                    }, 1500);
                }

            })

            .catch(function (error) {
                console.error(
                    "Search Add to Cart Error:",
                    error
                );
            });

        });

    });

});

// =========================================================
// REVIEW STAR SELECTION
// =========================================================

document.addEventListener("DOMContentLoaded", function () {

    const ratingStars = document.querySelectorAll(".rating-star");
    const reviewRating = document.getElementById("reviewRating");

    if (!ratingStars.length || !reviewRating) {
        return;
    }

    ratingStars.forEach(function (star) {

        star.addEventListener("click", function () {

            const selectedRating = parseInt(
                this.getAttribute("data-rating")
            );

            reviewRating.value = selectedRating;

            ratingStars.forEach(function (item) {

                const itemRating = parseInt(
                    item.getAttribute("data-rating")
                );

                if (itemRating <= selectedRating) {
                    item.classList.add("active");
                } else {
                    item.classList.remove("active");
                }

            });

        });

    });

});

// =========================================================
// SUBMIT CUSTOMER REVIEW
// =========================================================

async function submitReview(productId) {

    const ratingInput = document.getElementById("reviewRating");
    const commentInput = document.getElementById("reviewComment");
    const message = document.getElementById("reviewMessage");

    const rating = parseInt(ratingInput.value);
    const comment = commentInput.value.trim();

    if (!rating || rating < 1 || rating > 5) {
        message.textContent = "Please select a rating.";
        message.style.color = "#dc2626";
        return;
    }

    if (!comment) {
        message.textContent = "Please write your feedback.";
        message.style.color = "#dc2626";
        return;
    }

    if (comment.length < 5) {
        message.textContent = "Feedback must contain at least 5 characters.";
        message.style.color = "#dc2626";
        return;
    }

    if (comment.length > 1000) {
        message.textContent = "Feedback cannot exceed 1000 characters.";
        message.style.color = "#dc2626";
        return;
    }

    try {

        const response = await fetch(
            `/product/${productId}/review`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    rating: rating,
                    comment: comment
                })
            }
        );

        const data = await response.json();

        if (data.success) {

            message.textContent = data.message;
            message.style.color = "#15803d";

            commentInput.value = "";
            ratingInput.value = "0";

            document.querySelectorAll(".rating-star").forEach(function (star) {
                star.classList.remove("active");
            });

            setTimeout(function () {
                window.location.reload();
            }, 1000);

        } else {

            message.textContent = data.message;
            message.style.color = "#dc2626";

        }

    } catch (error) {

        console.error("Review submission error:", error);

        message.textContent =
            "Something went wrong. Please try again.";

        message.style.color = "#dc2626";
    }
}

document.addEventListener("DOMContentLoaded", function () {

    const wishlistButtons = document.querySelectorAll(".product-wishlist-btn, .image-wishlist-btn");

    wishlistButtons.forEach(function (button) {

        button.addEventListener("click", async function () {

            const productId = this.dataset.productId;

            if (!productId) {
                return;
            }

            try {

                const response = await fetch(
                    `/toggle-wishlist/${productId}`,
                    {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        }
                    }
                );

                const data = await response.json();

                if (data.login_required) {
                    window.location.href = "/login";
                    return;
                }

                if (!data.success) {
                    alert(data.message || "Something went wrong.");
                    return;
                }

                if (data.added) {
                    this.classList.add("active");
                    this.setAttribute("aria-label", "Remove from Wishlist");
                } else {
                    this.classList.remove("active");
                    this.setAttribute("aria-label", "Add to Wishlist");
                }

            } catch (error) {

                console.error("Wishlist error:", error);

                alert("Unable to update Wishlist.");
            }

        });

    });

});

// =========================================================
// WISHLIST REMOVE
// =========================================================

document.addEventListener("DOMContentLoaded", function () {

    const removeButtons = document.querySelectorAll(".wishlist-remove-btn");

    removeButtons.forEach(function (button) {

        button.addEventListener("click", async function () {

            const productId = this.dataset.productId;

            if (!productId) {
                return;
            }

            try {

                const response = await fetch(
                    `/toggle-wishlist/${productId}`,
                    {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        }
                    }
                );

                const data = await response.json();

                if (!data.success) {
                    alert(data.message || "Unable to remove product.");
                    return;
                }

                if (data.added === false) {

                    const card = this.closest(".wishlist-card");

                    if (card) {
                        card.remove();
                    }

                }

            } catch (error) {

                console.error("Wishlist remove error:", error);

                alert("Unable to remove product.");
            }

        });

    });

});

// =========================================================
// FEEDBACK PAGE INTERACTIONS
// =========================================================

document.addEventListener("DOMContentLoaded", function () {

    // Character Counter
    const messageBox = document.getElementById("message");
    const characterCount = document.getElementById("characterCount");

    if (messageBox && characterCount) {

        function updateCharacterCount() {
            const currentLength = messageBox.value.length;

            characterCount.textContent =
                currentLength + " / 500";

            if (currentLength >= 450) {
                characterCount.style.color = "#d97706";
            } else {
                characterCount.style.color = "#9ca3af";
            }

            if (currentLength >= 500) {
                characterCount.style.color = "#dc2626";
            }
        }

        messageBox.addEventListener(
            "input",
            updateCharacterCount
        );

        updateCharacterCount();
    }


    // Star Rating Text
    const ratingInputs =
        document.querySelectorAll(
            '.star-rating input[name="rating"]'
        );

    const ratingText =
        document.getElementById("ratingText");

    if (ratingInputs.length && ratingText) {

        const ratingMessages = {
            "1": "Poor — We'll work to improve.",
            "2": "Fair — Thanks for sharing.",
            "3": "Good — We appreciate your feedback.",
            "4": "Very Good — We're glad you enjoyed it.",
            "5": "Excellent — Thank you for your support!"
        };

        ratingInputs.forEach(function (input) {

            input.addEventListener("change", function () {

                ratingText.textContent =
                    ratingMessages[this.value];

                ratingText.style.color = "#ff9900";
                ratingText.style.fontWeight = "600";
            });

        });
    }

});