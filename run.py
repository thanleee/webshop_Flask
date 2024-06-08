from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
import os
app = Flask(__name__)

app.config['MYSQL_HOST']='127.0.0.1'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='123456789'
app.config['MYSQL_DB']='tmdt'


mysql = MySQL(app)


def get_last_name(email):
    cur = mysql.connection.cursor()
    cur.execute("SELECT last_name FROM customers WHERE email_address = %s", (email,))
    last_name = cur.fetchone()[0]
    cur.close()
    return last_name

def get_role(email):
    cur = mysql.connection.cursor()
    cur.execute("SELECT role FROM customers WHERE email_address = %s", (email,))
    role = cur.fetchone()[0]
    cur.close()
    return role
def get_category():
    cur = mysql.connection.cursor()
    category= "select * from tmdt.category ORDER BY cate_id ASC"
    cur.execute(category)
    datacate=cur.fetchall()
    cur.close()
    return datacate
def get_color():
    cur = mysql.connection.cursor()
    cur.execute("SELECT DISTINCT color FROM tmdt.products ORDER BY color ASC")
    colors = cur.fetchall()
    cur.close()
    return colors

def get_order_list(orders):
    cur = mysql.connection.cursor()
    history_order = []

    for order in orders:
        cartID = order[1]
        cusID=order[0]
        billID = order[2]
        cur.execute("SELECT name,image_1 FROM tmdt.products WHERE product_id=%s", (order[3],))
        productdetail=cur.fetchone()
        nameProduct =productdetail[0]
        image=productdetail[1]
        cur.execute("SELECT status_order,order_total FROM tmdt.bill where bill_id=%s;", (billID,))
        getbill = cur.fetchone()
        ordertotal=getbill[1]
        statusOrder = getbill[0]

        # Check if the current billID already exists in history_order
        found = False
        for data in history_order:
            if data['billID'] == billID:
                found = True
                product_info = {
                    'quantity': order[4],
                    'nameProduct': nameProduct,
                    'unitPrice': order[5],
                    'image':image
                }
                data['products'].append(product_info)
                break

        # If the current billID is not found in history_order, create a new entry
        if not found:
            product_info = {
                'quantity': order[4],
                'nameProduct': nameProduct,
                'unitPrice': order[5],
                'image':image
            }
            new_entry = {
                'billID': billID,
                'cusID': cusID,
                'statusOrder': statusOrder,
                'totalPrice':  ordertotal,
                'products': [product_info]
            }
            history_order.append(new_entry)
    cur.close()
    return history_order


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    
    datacate=get_category()
    if request.method == 'POST':
        userDetails = request.form
        fname = userDetails['fname']
        lname = userDetails['lname']
        phone = userDetails['phone']
        email = userDetails['email']
        password = userDetails['password']
        
        cur = mysql.connection.cursor()
        # Kiểm tra xem số điện thoại đã tồn tại trong cơ sở dữ liệu hay chưa
        cur.execute("SELECT * FROM customers WHERE contact = %s or email_address = %s", (phone,email))
        existing_user = cur.fetchone()
        
        if existing_user:
            cur.close()
            return redirect('/signup')
        else:
            cur.execute("INSERT INTO customers (first_name, last_name, contact, email_address, password,role) VALUES (%s, %s, %s, %s, %s,'Customer')", (fname, lname, phone, email, password))
            mysql.connection.commit()
            cur.close()
            return redirect('/women')

    return render_template('sign-up_header-women.html',category=datacate)

@app.route('/login', methods=['GET', 'POST'])
def login():
    data = None
    cur = mysql.connection.cursor()

    query = "select * from tmdt.products ORDER BY product_id ASC"
    cur.execute(query)
    data = cur.fetchall()

    cur.execute("SELECT DISTINCT color FROM tmdt.products ORDER BY color ASC")
    colors = cur.fetchall()
    pp = ["0 - 10",
      "10 - 20",
      "20 - 30",
      "30 - 50",
      "50 - 100",
      "100 - 500"]
    datacate=get_category()
    if request.method == 'POST':
        userDetails = request.form
        email = userDetails['email']
        password = userDetails['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM tmdt.customers WHERE email_address = %s AND password = %s", (email, password))
        user = cur.fetchone()
        cur.close()

        if user:
            session['email'] = email
            session['cusID'] = user[0]
            return redirect('/women')
        else:
            return redirect('/signup')
    colo = [False] * len(colors)
    price_checkboxes = [False] * len(pp)
    return render_template('women.html', products=data, category=datacate,colors= colors,colo=colo,pp=pp,price_checkboxes=price_checkboxes)

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect('/women')

@app.route('/updateinfor', methods=['GET', 'POST'])
def updateinfor():
    datacate = get_category()

    last_name = None
    role = None
    if 'email' in session:
        email = session['email']
        last_name = get_last_name(email)
        role=get_role(email)
        # Kết nối tới cơ sở dữ liệu
        cur = mysql.connection.cursor()
        
        # Thực hiện truy vấn SQL để lấy thông tin của người dùng dựa trên email
        cur.execute("SELECT * FROM customers WHERE email_address = %s", (email,))
        user_data = cur.fetchone()
        
        cur.close()
        
        # Kiểm tra xem có dữ liệu người dùng được trả về từ cơ sở dữ liệu không
        if user_data:
            # Chuyển đổi dữ liệu từ tuple sang dictionary
            user_data_dict = {
                'phone': user_data[8],  # Chỉ số của cột 'contact'
                'email': user_data[5],  # Chỉ số của cột 'email_address'
                'fname': user_data[1],  # Chỉ số của cột 'first_name'
                'lname': user_data[2],  # Chỉ số của cột 'last_name'
                'gender': user_data[3],  # Chỉ số của cột 'gender'
                'date': user_data[4].strftime('%Y-%m-%d') if user_data[4] else ''  # Chỉ số của cột 'birthday'
            }
        else:
            # Trong trường hợp không tìm thấy thông tin người dùng, khởi tạo dữ liệu trống
            user_data_dict = {}
    else:
        # Trong trường hợp không có email trong session, khởi tạo dữ liệu trống
        user_data_dict = {}

    return render_template('update_infor.html', user=user_data_dict, last_name=last_name, category=datacate,get_role=role)

@app.route('/change', methods=['POST'])
def update_customer():
    if request.method == 'POST':
        # Xử lý cập nhật thông tin người dùng ở đây
        
        phone = request.form['phone']
        email = request.form['email']
        first_name = request.form['fname']
        last_name = request.form['lname']
        gender = request.form['gender']
        birthday = request.form['date']
        
        customer_id = session['cusID']
        cur = mysql.connection.cursor()
        # cur.execute("UPDATE customers SET first_name = %s, last_name = %s, contact = %s, email_address = %s, gender = %s, birthday = %s WHERE email_address = %s", (first_name, last_name, phone, email, gender, birthday, email))
        cur.execute("UPDATE customers SET first_name = %s, last_name = %s, contact = %s, email_address = %s, gender = %s, birthday = %s WHERE customer_id = %s", (first_name, last_name, phone, email, gender, birthday, customer_id))
        mysql.connection.commit()
        cur.close()
        
        # Sau khi cập nhật thành công, chuyển hướng người dùng đến trang khác
        return redirect(url_for('updateinfor'))  # Chuyển hướng đến route có tên 'updateinfor'
    else:
        return 'Method Not Allowed', 405  # Trả về lỗi 405 nếu phương thức không phải là POST


@app.route('/changepassword')
def changepassword():

    datacate=get_category()
    role = None
    if 'email' in session:
        email = session['email']
        last_name = get_last_name(email)
        role=get_role(email)
    return render_template('password_change.html', last_name=last_name,category=datacate,get_role=role)

@app.route('/changepass', methods=['POST'])
def changepassword_post():
    if request.method == 'POST':
        # Lấy thông tin từ form
        old_password = request.form['oldpass']
        new_password = request.form['password']
        confirm_password = request.form['cfpassword']
        
        #Kiểm tra xác nhận mật khẩu
        # if new_password != confirm_password:
        #     return 'Passwords do not match!', 400
        if new_password != confirm_password:
            # Sử dụng alert để hiển thị cảnh báo
            return '''
            <script>
                alert('Passwords do not match!');
                window.location.href = '/changepassword'; // Chuyển hướng về trang web ban đầu
            </script>
            '''
        
        # Kiểm tra mật khẩu cũ
        email = session.get('email')
        if not email:
            return redirect(url_for('login'))  # Nếu không có email trong session, chuyển hướng đến trang login
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT password FROM customers WHERE email_address = %s", (email,))
        user_data = cur.fetchone()
        cur.close()
        
        if not user_data or user_data[0] != old_password:
            # return 'Incorrect old password!', 400
            return '''
            <script>
                alert('Passwords not correct !');
                window.location.href = '/changepassword'; // Chuyển hướng về trang web ban đầu
            </script>
            '''
        
        # Thực hiện cập nhật mật khẩu mới vào cơ sở dữ liệu
        cur = mysql.connection.cursor()
        cur.execute("UPDATE customers SET password = %s WHERE email_address = %s", (new_password, email))
        mysql.connection.commit()
        cur.close()
        
        return redirect(url_for('getorder'))
    else:
        return 'Method Not Allowed', 405  # Trả về lỗi 405 nếu phương thức không phải là POST



@app.route('/women', methods=['GET', 'POST'])
def women():
    cur = mysql.connection.cursor()
    datacate=get_category()
    colors = get_color()
    pp = ["0 - 10",
      "10 - 20",
      "20 - 30",
      "30 - 50",
      "50 - 100",
      "100 - 500"]
    if 'email' in session:
        email = session['email']
        last_name = get_last_name(email)
        
        cur.execute("SELECT * FROM tmdt.products ORDER BY product_id ASC")
        products = cur.fetchall()
        cur.close()
        colo = [False] * len(colors)
        price_checkboxes = [False] * len(pp)
        return render_template('women.html', last_name=last_name, products=products,category=datacate, colors= colors,colo=colo,pp=pp,price_checkboxes=price_checkboxes)
    else:
        return redirect('/login')

@app.route('/category/<id>', methods=['GET', 'POST'])
def category(id):  # Thêm tham số id vào hàm xử lý
    cur = mysql.connection.cursor()
    datacate = get_category()
    colors = get_color()
    pp = ["0 - 10",
      "10 - 20",
      "20 - 30",
      "30 - 50",
      "50 - 100",
      "100 - 500"]
    category= "select category_name from tmdt.category where cate_id=%s"
    cur.execute(category,(id,))
    current_category_name= cur.fetchone()[0]
    last_name=None
    if 'email' in session:
        email = session['email']
        last_name = get_last_name(email)

    cur.execute("SELECT * FROM tmdt.products WHERE category_id=%s", (id,))
    getProductByCategory = cur.fetchall()
    cur.close()
    colo = [False] * len(colors)
    price_checkboxes = [False] * len(pp)
    print(current_category_name)
    print(datacate)
    return render_template('women.html', getProductByCategory=getProductByCategory, category=datacate,last_name=last_name,current_category_name=current_category_name,colors=colors, colo=colo,pp=pp,price_checkboxes=price_checkboxes)

@app.route('/search', methods=['GET'])
def search():
    cur = mysql.connection.cursor()
    datacate = get_category()
    colors = get_color()
    search_text = request.args.get('txt')  # Lấy văn bản được nhập từ trường input
    last_name=None
    pp = ["0 - 10",
      "10 - 20",
      "20 - 30",
      "30 - 50",
      "50 - 100",
      "100 - 500"]
    if 'email' in session:
        email = session['email']
        last_name = get_last_name(email)

    # Tạo từ điển ánh xạ tên màu vào vị trí trong danh sách màu
    color_index_mapping = {color[0]: index for index, color in enumerate(colors)}
    # Khởi tạo mảng colo để lưu trạng thái checkbox
    colo = [False] * len(colors)
    # Kiểm tra xem trường input tìm kiếm có nội dung không
    
    price_index_mapping = {price: index for index, price in enumerate(pp)}
    price_checkboxes = [False] * len(pp)

    if search_text:
        search_text = search_text.upper()
        cur.execute("SELECT * FROM tmdt.products WHERE name LIKE %s", ('%' + search_text + '%',))
        search_results = cur.fetchall()
    else:
        # Nếu không có nội dung, thực hiện tìm kiếm theo màu sắc
        selected_colors = request.args.getlist('color')  # Lấy danh sách các tên màu đã chọn
        selected_prices = request.args.getlist('price')

        if selected_colors:
            # Đánh dấu các checkbox tương ứng với màu đã chọn
            for color_name in selected_colors:
                if color_name in color_index_mapping:
                    colo[color_index_mapping[color_name]] = True
            # Tạo danh sách placeholders cho số lượng màu sắc được chọn
            placeholders = ', '.join(['%s' for _ in selected_colors])
            # Tạo câu truy vấn SQL để lấy tất cả sản phẩm có màu sắc được chọn
            query = "SELECT * FROM tmdt.products WHERE color IN ({})".format(placeholders)
            # Thực hiện câu truy vấn SQL với danh sách màu sắc được chọn
            cur.execute(query, selected_colors)
            search_results = cur.fetchall()
        elif selected_prices:
            # Đánh dấu các checkbox tương ứng với giá đã chọn
            price_ranges = []
            for price_range in selected_prices:
                min_price, max_price = map(int, price_range.split(' - '))
                price_ranges.append((min_price, max_price))
                if price_range in price_index_mapping:
                    price_checkboxes[price_index_mapping[price_range]] = True
            # Tạo danh sách placeholders cho số lượng khoảng giá được chọn
            placeholders = ', '.join(['%s' for _ in price_ranges])

            # Tạo câu truy vấn SQL để lấy tất cả sản phẩm có giá trong các khoảng giá được chọn
            query = "SELECT * FROM tmdt.products WHERE "
            conditions = []
            for min_price, max_price in price_ranges:
                conditions.append("(price >= {} AND price <= {})".format(min_price, max_price))
            query += " OR ".join(conditions)

            # Thực hiện câu truy vấn SQL với danh sách giá được chọn
            cur.execute(query)
            search_results = cur.fetchall()
        else:
            # Nếu không có màu sắc hoặc giá được chọn, trả về tất cả sản phẩm
            cur.execute("SELECT * FROM tmdt.products")
            search_results = cur.fetchall()

    cur.close()
    # Truyền biến `colo` vào template
    return render_template('women.html', search_results=search_results, search_text=search_text, colors=colors, colo=colo, price_checkboxes=price_checkboxes, category=datacate, last_name=last_name,pp=pp)

@app.route('/products/<id>', methods=['GET', 'POST'])

def products(id): 
    
    cur = mysql.connection.cursor()
    datacate=get_category()
    cur.execute("UPDATE tmdt.products SET view = view + 1 WHERE product_id = %s", (id,))
    mysql.connection.commit()

    if 'email' in session:
        email = session['email']
        last_name = get_last_name(email)

        cur.execute("select * from tmdt.products where product_id = '{}'".format(id))
        data = cur.fetchone()
        if data is not None:
            size=data[8]
            color=data[4]
            stock=float(data[5])
            if data[12] is not None:
                discount = float(data[12]) 
                unitPrice = round(data[3] - (data[3] * discount / 100), 1)
            else:
                unitPrice=data[3]
            
            cur.execute("SELECT customer_id FROM customers WHERE email_address = %s", (email,))
            cusID = cur.fetchone()[0]
            productID=id

            if request.method == 'POST' and request.form['action'] == 'Addtocart':
                getquantity = request.form
                quantity= float(getquantity['quantity'])
                totalPrice = unitPrice*quantity
                cusID = int(cusID)
                status = None
                if stock > 0 and quantity <= stock:
                    cur.execute("SELECT * FROM tmdt.cart WHERE customer_id = %s AND product_id = %s AND status='notcheckedout'", (cusID, productID))
                    existing_cart_item = cur.fetchone()
                    if existing_cart_item:
        # Nếu có mục trùng, cập nhật cột quantity_product của mục đó bằng giá trị quantity mới cộng với quantity_product hiện có
                        new_quantity = float(existing_cart_item[3] + quantity)
                        if new_quantity > stock:
                            status=0
                        else:
                            totalPrice = unitPrice*new_quantity
                            cur.execute("UPDATE tmdt.cart SET quantity_product = %s , total_price=%s WHERE customer_id = %s AND product_id = %s ", (new_quantity,totalPrice, cusID, productID))
                            mysql.connection.commit()
                            status = 1
                    else:
        # Nếu không có mục trùng, thêm một mục mới vào bảng cart với thông tin mới
                        cur.execute("INSERT INTO tmdt.cart (customer_id, product_id, quantity_product, unit_price, total_price, size, color, status) VALUES (%s, %s, %s, %s, %s, %s, %s, 'notcheckedout')", (cusID, productID, quantity, unitPrice, totalPrice, size, color))
                        mysql.connection.commit()
                        status = 2
                    cur.close()
                    return render_template('productdetail.html',last_name=last_name, productdetail=data, status=status,category=datacate)
                else:
                    return render_template('productdetail.html',last_name=last_name, productdetail=data, status=status,category=datacate)
        return render_template('productdetail.html',last_name=last_name, productdetail=data,category=datacate)

        

    query = "select * from tmdt.products where product_id = '{}'".format(id)
    cur.execute(query)
    data = cur.fetchone()
    cur.close()
    
    return render_template('productdetail.html', productdetail=data,category=datacate)

@app.route('/cart', methods=['GET', 'POST'])
def cart(): 
    
    cur = mysql.connection.cursor()
    datacate=get_category()

    if 'email' in session:
        email = session['email']
        last_name = get_last_name(email)

        cur.execute("SELECT customer_id FROM customers WHERE email_address = %s", (email,))
        cusID = cur.fetchone()[0]
        cusID = int(cusID)

        getcart = "SELECT name, price, stock,  c.size,c.color, image_1, discount, c.cart_id,c.quantity_product,c.product_id FROM tmdt.products p INNER JOIN tmdt.cart c ON p.product_id = c.product_id where customer_id= '{}' AND c.status = 'notcheckedout'  order by c.cart_id DESC".format(cusID)
        cur.execute(getcart)
        datacart = cur.fetchall()
        cart_items = []
        totalPrice=0
        totalPricesale=0
        for item in datacart:
            name = item[0]
            price = float(item[1])
            stock = round(float(item[2]))
            size = item[3]
            color = item[4]
            image = item[5]
            discount = item[6]
            cartID= item[7]
            qty=round(float(item[8]))
            productID=item[9]
            discount = float(item[6]) if item[6] is not None else None
            if discount is not None:
                discounted_price = round(price - (price * discount / 100), 1)
            else:
                discounted_price = price
            if stock >= qty :  
                totalPriceOneofP= qty* price
                totalPrice=totalPrice + totalPriceOneofP
                session['totalPrice'] = totalPrice
                totalPriceOneofPSale= qty* discounted_price
                totalPricesale= round(totalPricesale + totalPriceOneofPSale,1)
                session['totalPricesale'] = totalPricesale
           
            cart_item = {
                'name': name,
                'price': price,
                'discounted_price': discounted_price,
                'stock': stock,
                'size': size,
                'color': color,
                'image': image,
                'discount': discount,
                'cartID': cartID,
                'qty':qty,
                'productID': productID
            }
            cart_items.append(cart_item)

        print("Total Price:", totalPrice)
        print("Total Pricesale:", totalPricesale)
        sale=round(totalPrice- totalPricesale,1)
        session['sale'] = sale
        session['cart_items']=cart_items
        cur.close()
        return render_template('cart.html', last_name=last_name, cart_items=cart_items,category=datacate,totalPrice=totalPrice,totalPricesale=totalPricesale, sale=sale)
    
@app.route('/deletecart/<id>', methods=['GET', 'POST'])
def delProductFromCart(id): 
    if 'email' in session:
        cur = mysql.connection.cursor()     
        cur.execute("DELETE FROM tmdt.cart WHERE cart_id ='{}'".format(id))
        mysql.connection.commit()
        cur.close()
        return redirect('/cart')
    
@app.route('/updatecart/<id>', methods=['GET', 'POST'])
def updateCart(id): 
    if 'email' in session:
        cartupdate = request.form
        quantity= cartupdate['quantity']
        quantity=round(float(quantity))
        cur = mysql.connection.cursor()
        cur.execute("SELECT unit_price FROM tmdt.cart WHERE cart_id = %s", (id,))
        unitprice_tuple = cur.fetchone()  # Fetch the result as a tuple
        if unitprice_tuple:  # Check if there is a result
            unitprice = float(unitprice_tuple[0])  # Extract value from tuple and convert to float
            totalprice = unitprice * quantity

            cur.execute("UPDATE tmdt.cart SET quantity_product = %s, total_price = %s WHERE cart_id = %s", (quantity, totalprice, id))
            mysql.connection.commit()
            cur.close()
        mysql.connection.commit()
        cur.close()
        return redirect('/cart')
    
@app.route('/checkout', methods=['GET', 'POST'])
def checkout(): 
    if 'email' in session:
        total = session.get('totalPrice', 0)  # Retrieve totalPrice from session
        totalPricesale = session.get('totalPricesale', 0)
        sale = session.get('sale', 0)
        cur=mysql.connection.cursor()
        cur.execute("SELECT * FROM tmdt.courier ")
        courier=cur.fetchall()
        cart_items=session.get('cart_items')
        print(cart_items)
        cur.close()
        return render_template('payment.html', total=total,totalPricesale=totalPricesale,sale=sale,courier=courier)
    
@app.route('/order', methods=['GET', 'POST'])  
def order(): 
    if 'email' in session:
        if request.method == 'POST':
            orderdetail = request.form
            name = orderdetail['name']
            email = orderdetail['email']
            phone = orderdetail['phone']
            address = orderdetail['address']
            courier_method= orderdetail['shippingMethod']
            courier_name=courier_method.split('-')[0]
            courier_fee = courier_method.split('$')[1]
            total_price= orderdetail['total']
            sale= orderdetail['pricesale']
            order_total= orderdetail['totalorder']
            payment_method= orderdetail['paymentMethod']
            
            cur = mysql.connection.cursor()     
            sql = "INSERT INTO tmdt.bill (name, email, phone, address, name_courier, courier_fee, total_price, sale, order_total, method_payment,status_payment,status_order) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,'Chua thanh toán','Chờ xác nhận')"
            val = (name, email, phone, address, courier_name, courier_fee, total_price, sale, order_total, payment_method)
            cur.execute(sql, val)
            mysql.connection.commit()
            bill_id = cur.lastrowid
            cart_items = session.get('cart_items')
            print("Bill:",bill_id)
            for item in cart_items:
                sql_order = "INSERT INTO tmdt.orders (cart_id, bill_id) VALUES (%s, %s)"
                val_order = (item['cartID'], bill_id)
                cur.execute(sql_order, val_order)

                sql_update_cart = "UPDATE cart SET status = 'checkedout' WHERE cart_id = %s"
                cur.execute(sql_update_cart, (item['cartID'],))

                product_id = item['productID']
                quantity_product = item['qty']
                
                # Trừ đi số lượng đã bán khỏi số lượng tồn kho
                sql_update_stock = "UPDATE tmdt.products SET stock = stock - %s,total_goods_sold = total_goods_sold + %s WHERE product_id = %s"
                cur.execute(sql_update_stock, (quantity_product, quantity_product,product_id))
                mysql.connection.commit()
            cur.close()
            return redirect('/getorder')


@app.route('/getorder', methods=['GET', 'POST'])  
def getorder():
    if 'email' in session:
        email = session['email']
        last_name = get_last_name(email)
        role=get_role(email)
        cusID = session.get('cusID')
        cur = mysql.connection.cursor()
        cur.execute("select c.customer_id, o.cart_id, o.bill_id, c.product_id, c.quantity_product, c.unit_price, c.total_price from tmdt.cart c inner join tmdt.orders o on c.cart_id=o.cart_id where customer_id = %s ORDER BY o.bill_id DESC",(cusID,))
        orders = cur.fetchall()
        history_order=get_order_list(orders)
        #print(history_order)
        session['history_order'] = history_order
        cur.close()
        return render_template('historyorder.html', history_order=history_order, last_name=last_name,get_role=role)
    

# @app.route('/getorder', methods=['GET', 'POST'])  
# def getorder():
#     if 'email' in session:
#         email = session['email']
#         last_name = get_last_name(email)
#         role=get_role(email)
#         cusID = session.get('cusID')
#         cur = mysql.connection.cursor()
#         cur.execute("select c.customer_id, o.cart_id, o.bill_id, c.product_id, c.quantity_product, c.unit_price, c.total_price from tmdt.cart c inner join tmdt.orders o on c.cart_id=o.cart_id where customer_id = %s ORDER BY o.bill_id DESC",(cusID,))
#         orders = cur.fetchall()
#         history_order = []
        
#         for order in orders:
#             cartID = order[1]
#             billID = order[2]
#             cur.execute("SELECT name,image_1 FROM tmdt.products WHERE product_id=%s", (order[3],))
#             productdetail=cur.fetchone()
#             nameProduct =productdetail[0]
#             image=productdetail[1]
#             cur.execute("SELECT status_order,order_total FROM tmdt.bill where bill_id=%s;", (billID,))
#             getbill = cur.fetchone()
#             ordertotal=getbill[1]
#             statusOrder = getbill[0]

#             # Check if the current billID already exists in history_order
#             found = False
#             for data in history_order:
#                 if data['billID'] == billID:
#                     found = True
#                     product_info = {
#                         'quantity': order[4],
#                         'nameProduct': nameProduct,
#                         'unitPrice': order[5],
#                         'image':image
#                     }
#                     data['products'].append(product_info)
#                     break

#             # If the current billID is not found in history_order, create a new entry
#             if not found:
#                 product_info = {
#                     'quantity': order[4],
#                     'nameProduct': nameProduct,
#                     'unitPrice': order[5],
#                     'image':image
#                 }
#                 new_entry = {
#                     'billID': billID,
#                     'statusOrder': statusOrder,
#                     'totalPrice':  ordertotal,
#                     'products': [product_info]
#                 }
#                 history_order.append(new_entry)
#         #print(history_order)
#         session['history_order'] = history_order
#         cur.close()
#         return render_template('historyorder.html', history_order=history_order, last_name=last_name,get_role=role)
    
@app.route('/getbill/<id>', methods=['GET', 'POST'])
def getbill(id): 
    if 'email' in session:
        email = session['email']
        last_name = get_last_name(email)
        role=get_role(email)
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM tmdt.bill WHERE bill_id=%s;", (id,))
        billdetail = cur.fetchone()
        cur.execute("SELECT cart_id FROM tmdt.orders WHERE bill_id=%s;", (id,))
        cart_ids = cur.fetchall()
        
        products_info = []
        for cart_id in cart_ids:
            cur.execute("SELECT product_id, quantity_product, unit_price,size,color FROM tmdt.cart WHERE cart_id=%s;", (cart_id,))
            product_info = cur.fetchone()
            if product_info:
                product_id, quantity, unit_price,size,color = product_info
                cur.execute("SELECT * FROM tmdt.products WHERE product_id=%s;", (product_id,))
                product_detail = cur.fetchone()
                if product_detail:
                    product_info = {
                        'product_id': product_id,
                        'name': product_detail[1],
                        'image': product_detail[10],
                        'quantity': quantity,
                        'unit_price_sale': unit_price,
                        'unit_price': product_detail[3],
                        'size': size,
                        'color': color
                        # Add other details you need
                    }
                    products_info.append(product_info)
        
        print(billdetail)
        print( products_info)
        return render_template('order_detail.html', billdetail=billdetail, products_info=products_info,last_name=last_name,get_role=role)

@app.route('/cancelorder/<id>', methods=['GET', 'POST'])
def cancelOrder(id): 
    if 'email' in session:
        cur = mysql.connection.cursor()     
        cur.execute("UPDATE tmdt.bill  SET status_order='Yêu cầu hủy đơn' WHERE bill_id=%s", (id,))
        mysql.connection.commit()
        cur.close()
        return redirect('/getorder')
# -----------admin-----------

@app.route('/usermanage', methods=['GET', 'POST'])
def usermanage():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tmdt.customers ORDER BY customer_id ASC")
    customer = cur.fetchall()
    cur.close()
    return render_template('admin/usermn.html', customer=customer)

@app.route('/permissionsuser/<id>', methods=['GET', 'POST'])
def manageupdateuser(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tmdt.customers WHERE customer_id = '{}'".format(id))
    customerdata = cur.fetchone()
    cur.close()
    return render_template('admin/permissionsuser.html', customerdata=customerdata) 

@app.route('/updateus/<id>', methods=['GET', 'POST'])
def updateus(id):
    userupdate = request.form
    role = userupdate['role']
    cur = mysql.connection.cursor()
    cur.execute("UPDATE customers SET role=%s WHERE customer_id=%s",(role, id))
    mysql.connection.commit()
    cur.close()
    return redirect('/usermanage')

@app.route('/deleteus/<id>', methods=['GET', 'POST'])
def deleteus(id):
    cur = mysql.connection.cursor()     
    cur.execute("DELETE FROM tmdt.customers WHERE customer_id ='{}'".format(id))
    mysql.connection.commit()
    cur.close()
    return redirect('/usermanage')
@app.route('/mnorder', methods=['GET', 'POST'])
def manage_order():
    if 'email' in session:
        email = session['email']
        last_name = get_last_name(email)
        role=get_role(email)
        cusID = session.get('cusID')
        cur = mysql.connection.cursor()
        cur.execute("select c.customer_id, o.cart_id, o.bill_id, c.product_id, c.quantity_product, c.unit_price, c.total_price from tmdt.cart c inner join tmdt.orders o on c.cart_id=o.cart_id ORDER BY o.bill_id DESC")
        orders = cur.fetchall()
        history_order=get_order_list(orders)
        session['history_order'] = history_order
        return render_template('admin/manageOrder.html', history_order=history_order, last_name=last_name, get_role=role)
    
@app.route('/confirmorder/<id>', methods=['GET', 'POST'])
def confirmOrder(id): 
    if 'email' in session:
        cur = mysql.connection.cursor()     
        cur.execute("UPDATE tmdt.bill  SET status_order='Chờ vận chuyển' WHERE bill_id=%s", (id,))
        mysql.connection.commit()
        cur.close()
        return redirect('/mnorder')

@app.route('/confircancelmorder/<id>', methods=['GET', 'POST'])
def confirmCancelOrder(id): 
    if 'email' in session:
        cur = mysql.connection.cursor()     
        cur.execute("UPDATE tmdt.bill  SET status_order='Đã hủy' WHERE bill_id=%s", (id,))
        mysql.connection.commit()
        cur.close()
        return redirect('/mnorder')
@app.route('/addproduct', methods=['GET', 'POST'])
def addproduct():
    if request.method == 'POST':
        # Lấy dữ liệu từ form
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        color = request.form['color']
        stock = request.form['stock']  # Chỉ nhập số lượng trong kho
        category_id = request.form['category_id']
        size = request.form['size']
        image_1 = request.files['image_1']
        image_2 = request.files['image_2']
        discount = float(request.form['discount'])

        if image_1 and image_2:
            # Đảm bảo đường dẫn tới thư mục tồn tại
            upload_folder = r'C:\Users\DELL\Desktop\testflask (1) (1)\testflask (1)\testflask\static\img'  # Đường dẫn tới thư mục upload
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)

            # Xử lý tệp tải lên và lưu vào thư mục
            image_1_filename = secure_filename(image_1.filename)
            image_2_filename = secure_filename(image_2.filename)
            image_1_path = os.path.join(upload_folder, image_1_filename)
            image_2_path = os.path.join(upload_folder, image_2_filename)
            image_1.save(image_1_path)
            image_2.save(image_2_path)

            # Kết nối tới cơ sở dữ liệu
            cur = mysql.connection.cursor()

            # Thực hiện INSERT vào cơ sở dữ liệu
            sql = "INSERT INTO products (name, description, price, color, stock, category_id, size, image_1, image_2, discount,total_goods_sold) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)"
            values = (name, description, price, color, stock, category_id, size, image_1_filename, image_2_filename, discount,0)
            cur.execute(sql, values)
            mysql.connection.commit()
            cur.close()
            # Chuyển hướng người dùng sau khi thêm sản phẩm thành công
            return redirect('/productmanage')
    else:
        # Nếu request method là 'GET', trả về template hiển thị form để thêm sản phẩm mới
        return render_template('admin/addproduct.html')



@app.route('/productmanage', methods=['GET', 'POST'])
def productmanage():

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM products ")
        productmn = cur.fetchall()
        return render_template('admin/productmanage.html', productmn=productmn)
# Route để hiển thị trang chỉnh sửa sản phẩm
from flask import render_template

@app.route('/updateproduct/<product_id>', methods=['GET'])
def updateproduct(product_id):
    # Assume you have a function to fetch product details from the database based on the product_id
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
    product = cur.fetchone()

    # Assume you have predefined lists for colors, category IDs, and sizes
    category_options = [1, 2, 3]  # Example list of category IDs
    cur.close()
    return render_template('admin/updateproduct.html', product=product, product_id=product_id, category_options=category_options)


@app.route('/updateproduct/<product_id>', methods=['POST'])
def updateproductsubmit(product_id):
    if request.method == 'POST':
        # Retrieve form data
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        color = request.form['color']
        stock = request.form['stock']
        # total_goods = request.form['total_goods']
        category_id = request.form['category_id']
        size = request.form['size']
        image_1 = request.files['image_1']
        image_2 = request.files['image_2']
        discount = request.form['discount']

        # Handle file uploads for image_1
        if image_1 and image_2:
            # Đảm bảo đường dẫn tới thư mục tồn tại
            upload_folder = r'C:\Users\DELL\Desktop\testflask (1) (1)\testflask (1)\testflask\static\img'  # Đường dẫn tới thư mục upload
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)

            # Xử lý tệp tải lên và lưu vào thư mục
            image_1_filename = secure_filename(image_1.filename)
            image_2_filename = secure_filename(image_2.filename)
            image_1_path = os.path.join(upload_folder, image_1_filename)
            image_2_path = os.path.join(upload_folder, image_2_filename)
            image_1.save(image_1_path)
            image_2.save(image_2_path)

        # Update product details in the database
        cur = mysql.connection.cursor()
        sql = "UPDATE products SET name = %s, description = %s, price = %s, color = %s, stock = %s, category_id = %s, size = %s,image_1 = %s,image_2=%s, discount = %s WHERE product_id = %s"
        val = (name, description, price, color, stock, category_id, size,image_1_filename, image_2_filename, discount, product_id)
        cur.execute(sql, val)
        mysql.connection.commit() 
        cur.close()

        # Chuyển hướng đến trang quản lý sản phẩm
    return redirect('/productmanage')
@app.route('/deleteproduct/<id>', methods=['GET', 'POST'])
def deleteproduct(id):
    cur = mysql.connection.cursor()     
    cur.execute("DELETE FROM products WHERE product_id =%s",(id,))
    mysql.connection.commit()
    cur.close()
    return redirect('/productmanage')
@app.route('/categorymanage', methods=['GET', 'POST'])
def categorymanage():
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM category ")
        category = cur.fetchall()
        return render_template('admin/categorymanage.html', category=category)
@app.route('/addcategory', methods=['GET', 'POST'])
def addcategory():
    if request.method == 'POST':
        category_name = request.form['category_name']
        cur = mysql.connection.cursor()
        sql = "INSERT INTO category (cate_id, category_name) VALUES (DEFAULT, %s)"  
        values = (category_name,)  
        cur.execute(sql, values)
        mysql.connection.commit()
        cur.close()
        return redirect('/categorymanage')  # Redirect to a success page or another page
    else:
        # If the request method is 'GET', return the template to display the form to add a new category
        return render_template('admin/addcategory.html')
@app.route('/updatecategory/<cate_id>', methods=['GET'])
def updatecategory(cate_id):
    # Assume you have a function to fetch product details from the database based on the product_id
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM category WHERE cate_id = %s", (cate_id,))
    category = cur.fetchone()
    cur.close()
    return render_template('admin/updatecategory.html', category=category, cate_id=cate_id)
@app.route('/updatecategory/<cate_id>', methods=['POST'])
def updatecategorysubmit(cate_id):
    if request.method == 'POST':
        # Retrieve form data
        category_name = request.form['category_name']
        cur = mysql.connection.cursor()
        sql = "UPDATE category SET category_name = %s WHERE cate_id = %s"
        val = (category_name,cate_id)
        cur.execute(sql, val)
        mysql.connection.commit()
        cur.close()
        
        # Redirect to category management page (assuming 'categorymanage' is the correct route)
        return redirect(url_for('categorymanage'))
@app.route('/deletecategory/<id>', methods=['GET', 'POST'])
def deletecategory(id):
    cur = mysql.connection.cursor()     
    cur.execute("DELETE FROM category WHERE cate_id =%s",(id,))
    mysql.connection.commit()
    cur.close()
    return redirect('/categorymanage')    
if __name__ == '__main__':
   
    app.secret_key = 'my_super_secret_key_171232'
    app.run(debug=True)
