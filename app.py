from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # for flashing messages

# In-memory data stores (demo purpose)
farm_data = {
    "Kammavari Palli": [],
    "P.C Palli": [],
    "Nethivaripallem": [],
    "Kandukur": []
}

# Customers list. Each customer has 'type', 'name', 'phone', 'area', 'farm_code'
customers = []

@app.route('/')
def root():
    return redirect(url_for('home'))

@app.route('/home')
def home():
    places = list(farm_data.keys())
    return render_template('home.html', places=places)

@app.route('/add-farm/<place>', methods=['GET', 'POST'])
def add_farm(place):
    if place not in farm_data:
        return f"Place '{place}' not found", 404

    if request.method == 'POST':
        farm_name = request.form.get('farm_name')
        farm_code = request.form.get('farm_code')

        existing_codes = [farm['farm_code'] for farm in farm_data[place]]
        if farm_code in existing_codes:
            flash("Farm code already exists for this place!", "error")
        elif farm_name and farm_code:
            farm_data[place].append({'farm_name': farm_name, 'farm_code': farm_code})
            return redirect(url_for('farm_customers', place=place, farm_code=farm_code))
        else:
            flash("Please fill in all fields.", "error")

    farms = farm_data[place]
    return render_template('add_farm.html', place=place, farms=farms)

@app.route('/farm-customers/<place>/<farm_code>')
def farm_customers(place, farm_code):
    farms = farm_data.get(place)
    if not farms:
        return "Place not found", 404

    farm = next((f for f in farms if f['farm_code'] == farm_code), None)
    if not farm:
        return "Farm not found", 404

    farm_customers = [c for c in customers if c.get('farm_code') == farm_code]
    return render_template('farm_customers.html', place=place, farm=farm, customers=farm_customers)

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Pre-fill values from query params if available
    place = request.args.get('place')
    farm_code = request.args.get('farm_code')
    customer_type = request.args.get('customer_type')

    if request.method == 'POST':
        customer_type = request.form.get('customer_type')
        name = request.form.get('name')
        phone = request.form.get('phone')
        area = request.form.get('area')
        farm_code = request.form.get('farm_code')
        place = request.form.get('place')  # ✅ Ensure 'place' is also retrieved from form

        if customer_type and name and phone and area and farm_code and place:
            customers.append({
                'type': customer_type,
                'name': name,
                'phone': phone,
                'area': area,
                'farm_code': farm_code
            })
            flash("Customer registered successfully!", "success")
            # ✅ Redirect to the list page of the registered customer type
            return redirect(url_for('customer_type_page', place=place, farm_code=farm_code, customer_type=customer_type))
        else:
            flash("Please fill in all fields.", "error")

    return render_template(
        'register.html',
        farm_data=farm_data,
        pre_place=place,
        pre_farm_code=farm_code,
        pre_type=customer_type
    )

@app.route('/customer-type/<place>/<farm_code>/<customer_type>')
def customer_type_page(place, farm_code, customer_type):
    filtered = [
        c for c in customers 
        if c.get('farm_code') == farm_code and c.get('type') == customer_type
    ]
    return render_template(
        'customer_list_by_type.html', 
        place=place, 
        farm_code=farm_code, 
        customer_type=customer_type, 
        customers=filtered
    )

if __name__ == '__main__':
    app.run(debug=True)
