# Gerekli kütüphaneler
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV
import streamlit as st

# 1. Veri Yükleme
file_path = 'CAR DETAILS FROM CAR DEKHO.csv'
car_data = pd.read_csv(file_path)

# 2. Kategorik Değişkenleri 1-0 Formatına Dönüştürme
car_data['fuel'] = car_data['fuel'].apply(lambda x: 1 if x == 'Diesel' else 0)  # Diesel -> 1, Petrol -> 0
car_data['transmission'] = car_data['transmission'].apply(lambda x: 1 if x == 'Automatic' else 0)  # Automatic -> 1, Manual -> 0

# Owner sütunlarını dönüştürme (True/False => 1/0)
car_data['owner_First Owner'] = car_data['owner'].apply(lambda x: 1 if x == 'First Owner' else 0)
car_data['owner_Second Owner'] = car_data['owner'].apply(lambda x: 1 if x == 'Second Owner' else 0)
car_data['owner_Third Owner'] = car_data['owner'].apply(lambda x: 1 if x == 'Third Owner' else 0)
car_data['owner_Fourth & Above Owner'] = car_data['owner'].apply(lambda x: 1 if x == 'Fourth & Above Owner' else 0)

# Owner'ın orijinal sütununu kaldırma
car_data.drop(columns=['owner'], inplace=True)

# seller_type sütununu sayısal formata dönüştürme
car_data['seller_type'] = car_data['seller_type'].apply(lambda x: 1 if x == 'Dealer' else 0)


# 3. Özellikler ve Hedef Değişken
X = car_data.drop(columns=['name', 'selling_price'])  # Model eğitimi için kullanılacak özellikler
y = car_data['selling_price']  # Tahmin edilecek hedef değişken

# 4. Eğitim ve Test Verisi Ayırma
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 5. Model Eğitimi için Hiperparametre Optimizasyonu (Grid Search)
param_grid = {
    'n_estimators': [100, 200],
    'max_depth': [20, 30],
    'min_samples_split': [2],
    'min_samples_leaf': [1]
}

grid_search = GridSearchCV(
    estimator=RandomForestRegressor(random_state=42),
    param_grid=param_grid,
    cv=3,
    verbose=1,
    n_jobs=-1
)

grid_search.fit(X_train, y_train)

# 6. En İyi Model ile Eğitme
best_params = grid_search.best_params_
final_model = RandomForestRegressor(**best_params, random_state=42)
final_model.fit(X_train, y_train)

st.title("Araç Fiyat Tahmin Modeli")
st.write("Lütfen araç bilgilerini girin ve tahmini fiyatı görün:")

# Kullanıcıdan giriş alma
year = st.slider("Araç Yılı", 2000, 2024, 2015)
km_driven = st.number_input("Kilometre (km):", min_value=0, step=1000, value=50000)
fuel = st.selectbox("Yakıt Türü", ["Petrol", "Diesel"])  # 0: Petrol, 1: Diesel
seller_type = st.selectbox("Satıcı Türü", ["Bireysel", "Bayi"])  # 0: Individual, 1: Dealer
transmission = st.selectbox("Vites Türü", ["Manual", "Automatic"])  # 0: Manual, 1: Automatic
owner = st.selectbox("Kaçıncı Sahibi", ["İlk", "İkinci", "Üçüncü", "Daha Fazla"])

# Tahmin yapma
if st.button("Tahmini Gör"):
    try:
        # Kullanıcı girişlerini modelin beklediği formata göre ayarla
        input_data = pd.DataFrame({
            "year": [year],
            "km_driven": [km_driven],
            "fuel": [1 if fuel == "Diesel" else 0],
            "seller_type": [1 if seller_type == "Bayi" else 0],
            "transmission": [1 if transmission == "Automatic" else 0],
            "owner_Second Owner": [1 if owner == "İkinci" else 0],
            "owner_Third Owner": [1 if owner == "Üçüncü" else 0],
            "owner_Fourth & Above Owner": [1 if owner == "Daha Fazla" else 0],
        })

        # Eğitim sırasında kullanılan sütunlar (X_train'den alınmalı)
        expected_columns = list(X_train.columns)

        # Eksik sütunları sıfır ile tamamlama
        for col in expected_columns:
            if col not in input_data.columns:
                input_data[col] = 0

        # Sütun sırasını eğitim sırasında kullanılan sıraya göre ayarla
        input_data = input_data[expected_columns]

        # Tahmini yap
        prediction = final_model.predict(input_data)[0]
        st.write(f"Tahmini Satış Fiyatı: {prediction:.2f} TL")
    except Exception as e:
        st.write(f"Hata: {e}")