# almutaweaa_insight 
# Olist Delivery Time Prediction

A machine learning project that predicts e-commerce delivery duration using the Brazilian Olist dataset. The project includes a simple Streamlit application that simulates an online shopping experience and provides estimated delivery times.

## Problem Statement

An analysis of 96,470 completed orders revealed that 91.9% arrived earlier than estimated, while 6.8% arrived late and only 1.3% arrived on time. This significant gap suggests that Olist's delivery estimates are often overly conservative and do not fully reflect its actual delivery performance, potentially affecting customer expectations and highlighting the need for more accurate estimates.

## Project Overview

- **Dataset:** Brazilian Olist E-commerce Dataset
- **Target:** Delivery duration in days
- **Baseline Model:** Linear Regression
- **Final Model:** Random Forest Regressor
- **Hyperparameter Tuning:** GridSearchCV
- **Evaluation Metric:** Mean Absolute Error (MAE)

## Features

**Order Information**
- `item_count`: Number of items in the order
- `seller_count`: Number of sellers involved
- `price_sum`: Total product price
- `freight_value_sum`: Total shipping cost

**Location**
- `distance_max`: Maximum seller-customer distance in kilometers

**Product Information**
- `product_max_dim_cm_max`: Maximum product dimension
- `product_vol_cm_max`: Maximum product volume

**Purchase Date**
- `purchase_month`: Month of purchase
- `purchase_day`: Day of the week

## Streamlit Application
https://olistdelivery.streamlit.app/
The application simulates a simple shopping journey:

1. Select products and quantities.
2. Enter customer information and select a location.
3. Choose an order date.
4. Place the order and view the estimated delivery duration, product total, and shipping cost.

## Technologies Used

- Python
- Pandas
- Scikit-learn
- Streamlit
- Joblib

## How to Run

**1. Install the required libraries**

```bash
pip install pandas scikit-learn streamlit joblib
```

**2. Run the application**

```bash
streamlit run delivery_app.py
```

**3. Required Files**


- `delivery_app.py`
- `delivery.pkl`
- `olist_products_dataset.csv`
- `olist_order_items_dataset.csv`
- `olist_sellers_dataset.csv`
- `olist_customers_dataset.csv`
- `olist_geolocation_dataset.csv`


## Future Improvements

- Product categories are used instead of individual product names.
- Some product or shipping details may require estimates when information is unavailable.
- Delivery predictions depend on the quality and coverage of the available dataset.
- Future improvements could include testing additional machine learning models and incorporating more relevant features.

## Team Members

- Wadeea
- Nouf
 
