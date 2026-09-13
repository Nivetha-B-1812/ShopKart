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

    if (totalElement) {
        totalElement.textContent =
            "₹" + subtotal.toLocaleString("en-IN", {
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