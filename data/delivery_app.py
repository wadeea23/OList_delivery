import streamlit as st
import pandas as pd
import joblib
from math import radians, sin, cos, asin, sqrt # i need it to cal langtide an latitude 

# Load model and data
model = joblib.load("data/delivery.pkl")
products = pd.read_csv("olist_products_dataset.csv")
items = pd.read_csv("olist_order_items_dataset.csv")
sellers = pd.read_csv("olist_sellers_dataset.csv")
customers = pd.read_csv("olist_customers_dataset.csv")
geo = pd.read_csv("olist_geolocation_dataset.csv")

# Features used by the model
cols = [
    "item_count", "seller_count", "price_sum",
    "freight_value_sum", "distance_max",
    "product_max_dim_cm_max", "product_vol_cm_max",
    "purchase_month", "purchase_day"
]

st.title("Brazilian Online Store")
st.write("Place your order and estimate your delivery time.")

# Prepare product data
product_info = items.groupby("product_id").agg({
    "price": "mean",
    "freight_value": "mean",
    "seller_id": "first"
}).reset_index()

product_info = product_info.rename(
    columns={"freight_value": "shipping"}
)

products = pd.merge(products, product_info, on="product_id")
products = pd.merge(
    products,
    sellers[["seller_id", "seller_zip_code_prefix"]],
    on="seller_id", how="left"
)

# Prepare location data
geo["zip"] = (
    pd.to_numeric(geo["geolocation_zip_code_prefix"], errors="coerce")
    .astype("Int64").astype(str).str.zfill(5)
)

geo = geo.groupby("zip").agg({
    "geolocation_lat": "mean",
    "geolocation_lng": "mean"
}).reset_index()

geo = geo.rename(columns={
    "geolocation_lat": "latitude",
    "geolocation_lng": "longitude"
})

# Choose products
st.subheader("1. Choose Your Products")

categories = {
    "Health and Beauty": "beleza_saude",
    "Beds and Bath": "cama_mesa_banho",
    "Computers": "informatica_acessorios",
    "Sports and Leisure": "esporte_lazer",
    "Watches and Gifts": "relogios_presentes",
    "Furniture": "moveis_decoracao",
    "Electronics": "eletronicos"
}

selected_products = st.multiselect(
    "Select products", list(categories.keys()) + ["Others"]
)

selected_rows = []

for i, name in enumerate(selected_products):
    if name == "Others":
        st.text_input("Enter product name", key="other_name")
        st.number_input(
            "Quantity for Others", min_value=1, value=1,
            key="quantity_other"
        )
    else:
        category_products = products[
            products["product_category_name"] == categories[name]
        ]

        quantity = st.number_input(
            f"Quantity for {name}", min_value=1, value=1,
            key=f"quantity_{i}"
        )

        if not category_products.empty:
            product = category_products.iloc[0].copy()
            product["quantity"] = quantity
            selected_rows.append(product)

selected = pd.DataFrame(selected_rows)

# Customer information
st.subheader("2. Customer Information")
name = st.text_input("Your Name")

state_names = {
    "AC": "Acre", "AL": "Alagoas", "AP": "Amapá",
    "AM": "Amazonas", "BA": "Bahia", "CE": "Ceará",
    "DF": "Distrito Federal", "ES": "Espírito Santo",
    "GO": "Goiás", "MA": "Maranhão", "MT": "Mato Grosso",
    "MS": "Mato Grosso do Sul", "MG": "Minas Gerais",
    "PA": "Pará", "PB": "Paraíba", "PR": "Paraná",
    "PE": "Pernambuco", "PI": "Piauí", "RJ": "Rio de Janeiro",
    "RN": "Rio Grande do Norte", "RS": "Rio Grande do Sul",
    "RO": "Rondônia", "RR": "Roraima", "SC": "Santa Catarina",
    "SP": "São Paulo", "SE": "Sergipe", "TO": "Tocantins"
}

states = sorted(customers["customer_state"].dropna().unique())

state = st.selectbox(
    "Select Brazilian State", states,
    format_func=lambda x: state_names.get(x, x)
)

cities = sorted(
    customers[customers["customer_state"] == state]
    ["customer_city"].dropna().unique()
)

city = st.selectbox("Select City", cities)

city_customers = customers[
    (customers["customer_state"] == state) &
    (customers["customer_city"] == city)
]

zip_codes = pd.to_numeric(
    city_customers["customer_zip_code_prefix"], errors="coerce"
).dropna()

zip_code = (
    str(int(zip_codes.iloc[0])).zfill(5)
    if not zip_codes.empty else ""
)

# Place order
if st.button("Order Now"):

    if not name.strip() or not selected_products:
        st.warning("Please complete all information.")

    elif "Others" in selected_products and not st.session_state.get(
        "other_name", ""
    ).strip():
        st.warning("Please enter your product name.")

    elif selected.empty:
        st.warning("Please choose an available product category.")

    elif not zip_code:
        st.warning("Could not find a ZIP code for this city.")

    else:
        item_count = int(selected["quantity"].sum())
        seller_count = selected["seller_id"].nunique()

        price_sum = (selected["price"] * selected["quantity"]).sum()
        shipping_sum = (
            selected["shipping"] * selected["quantity"]
        ).sum()

        # Find delivery distance
        selected["seller_zip"] = (
            pd.to_numeric(
                selected["seller_zip_code_prefix"], errors="coerce"
            ).astype("Int64").astype(str).str.zfill(5)
        )

        customer_location = geo[geo["zip"] == zip_code]
        distances = []

        if not customer_location.empty:
            for seller_zip in selected["seller_zip"]:
                seller_location = geo[geo["zip"] == seller_zip]

                if not seller_location.empty:
                    lat1 = customer_location.iloc[0]["latitude"]
                    lon1 = customer_location.iloc[0]["geolocation_lng"] if "geolocation_lng" in customer_location.columns else customer_location.iloc[0]["longitude"]
                    lat2 = seller_location.iloc[0]["latitude"]
                    lon2 = seller_location.iloc[0]["longitude"]

                    lat1, lon1, lat2, lon2 = map(
                        radians, [lat1, lon1, lat2, lon2]
                    )

                    a = (
                        sin((lat2-lat1)/2)**2 +
                        cos(lat1)*cos(lat2)*sin((lon2-lon1)/2)**2
                    )

                    distances.append(6371 * 2 * asin(sqrt(a)))

        if not distances:
            st.error("Could not calculate the delivery distance.")

        else:
            dimensions = selected[
                ["product_length_cm", "product_height_cm",
                 "product_width_cm"]
            ].fillna(0)

            today = pd.Timestamp.today()

            order = pd.DataFrame([{
                "item_count": item_count,
                "seller_count": seller_count,
                "price_sum": price_sum,
                "freight_value_sum": shipping_sum,
                "distance_max": max(distances),
                "product_max_dim_cm_max": dimensions.max(axis=1).max(),
                "product_vol_cm_max": (
                    selected["product_length_cm"].fillna(0) *
                    selected["product_height_cm"].fillna(0) *
                    selected["product_width_cm"].fillna(0)
                ).max(),
                "purchase_month": today.month,
                "purchase_day": today.weekday()
            }])

            prediction = model.predict(order[cols])[0]

            st.success("Order placed successfully!")
            st.write("Customer:", name)
            st.write("City:", city)
            st.write("State:", state_names.get(state, state))
            st.write(f"Product total: R$ {price_sum:.2f}")
            st.write(f"Shipping cost: R$ {shipping_sum:.2f}")
            st.write(f"Estimated delivery duration: {prediction:.1f} days")
