import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, jsonify
from fashion import app, db, bcrypt
from fashion.forms import RegistrationForm, LoginForm ,UpdateProfileForm , RecommendForm, PromptForm
from fashion.model import User, Info,Category, Item
from flask_login import login_user, current_user, logout_user, login_required


#------------------------------------------------------------------------
import nltk
from nltk.stem import PorterStemmer

from nltk.corpus import stopwords

#-------------------------------------------------------------------------
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

#---------------------------------------------------------------------------------
# import gensim
from fashion import google_model

# ------------------------------------------
import re
import random
import datetime

current_month = int(str(datetime.date.today())[5:7])
def seasons(month):
    if (10 <= month <= 12 or 1 <= month <= 4):
        return "winter"   
    elif (4 <= month <= 5):
        return "spring" 
    elif (6 <= month <= 9):
        return "summer"
    else:
        return "fall"
            
       

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/about")
def about():
    return render_template('about.html',title = "About")

@app.route("/register", methods = ['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('temp'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username = form.username.data, email = form.email.data, password = hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f"Account created! YOU CAN NOW LOGIN", 'primary')
        return redirect(url_for('login'))
    return render_template('register.html', title = 'Register', form = form)

@app.route("/login", methods = ['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('temp'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember = form.remember.data)
            flash('Login Successful, WELCOME', 'success')
            next_page =  request.args.get('next') # returns a dictionary of arguments of query eg({"next":"jdkljs",....})
            if user.info != None:
                return redirect (next_page) if next_page else redirect(url_for('temp'))
            else:
                return redirect(url_for('recommend'))
        else:
            flash('Login Unsuccessful, Please check email and password','danger') 
    
    return render_template('login.html', title = 'Login', form = form)

@app.route("/recommend", methods = ['GET','POST'])
def recommend():
    form = RecommendForm()
    if form.validate_on_submit():
        pattern = r'^\w+(,\w+)*$'
        if re.match(pattern, form.style.data ):
            pass
        else:
            flash("In Style_preference please type multiple choice seperated by ',' as shown ", 'danger')
            form.style.data = ""
            return render_template('recommend.html', title = 'Recommend', form = form)
    if form.validate_on_submit():
        pattern = r'^\w+(,\w+)*$'
        if re.match(pattern, form.color_preference.data ):
            pass
        else:
            flash("In Color_preference please type multiple choice seperated by ',' as shown ", 'danger')
            form.color_preference.data = ""
            return render_template('recommend.html', title = 'Recommend', form = form)
        info = Info(style_preference = form.style.data, body_type = form.body_type.data, gender = form.gender.data, color_preference = form.color_preference.data, user_id = current_user.id)
        db.session.add(info)
        db.session.commit()
        return redirect(url_for('temp'))
    return render_template('recommend.html', title = 'Recommend', form = form)
        
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _ , f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, "static/profile_pics", picture_fn)   

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


@app.route("/account", methods = ['GET','POST'])
@login_required
def account():
    # image_file = None
    form = UpdateProfileForm()
    if form.validate_on_submit():
        pattern = r'^\w+(,\w+)*$'
        if re.match(pattern, form.style.data ):
            pass
        else:
            
            flash("In Style_preference please type multiple choice seperated by ','", 'danger')
            form.style.data = ""
            image_file = url_for('static', filename = 'profile_pics/' + current_user.image_file)
            return render_template('account.html', title= 'Account', image_file = image_file , form = form)
        if re.match(pattern, form.color_preference.data ):
            pass

        else:
            flash("In Color_preference please type multiple choice seperated by ','", 'danger')
            form.color_preference.data = ""
            image_file = url_for('static', filename = 'profile_pics/' + current_user.image_file)
            return render_template('account.html', title= 'Account', image_file = image_file , form = form)
        
        if form.picture.data:
                picture_file = save_picture(form.picture.data)
                current_user.image_file = picture_file
        image_file = url_for('static', filename = 'profile_pics/' + current_user.image_file)
        

        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.info.style_preference = form.style.data
        current_user.info.body_type = form.body_type.data
        current_user.info.gender = form.gender.data
        current_user.info.color_preference = form.color_preference.data


        db.session.commit()
        flash('Account Updated Successfully','success')
        return render_template('account.html', title= 'Account', image_file = image_file , form = form)
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.style.data = current_user.info.style_preference
        form.body_type.data = current_user.info.body_type
        form.gender.data = current_user.info.gender
        form.color_preference.data = current_user.info.color_preference
    image_file = url_for('static', filename = 'profile_pics/' + current_user.image_file)
    return render_template('account.html', title= 'Account', image_file = image_file , form = form)


names = []
img_links = []
rates = []
pro_url = []

@app.route("/prompt" ,methods = ['GET','POST'])
@login_required
def prompt():

    err = 0
    global names, img_links, rates, pro_url
    form = PromptForm()
    if form.validate_on_submit():

        names.clear()
        img_links.clear()
        rates.clear()
        pro_url.clear()
        paragraph =  form.prompt.data
        print(paragraph)

        stem = PorterStemmer()
        sent = nltk.sent_tokenize(paragraph)
        print(sent)
        filtered_words = []

        for i in range(len(sent)):
            words = nltk.word_tokenize(sent[i])
            print(words)
            for word in words:
                if word not in set(stopwords.words('english')):
                    print(word)
                    print(stem.stem(word))
                    filtered_words.append(stem.stem(word))
        print(filtered_words)
        #------------------------------------------------------------------
        
        count = 0
        # for i in filtered_words:
        #     if google_model.similarity('fashion', i)*100 >13:
        #         count +=1                      
        
        # fashion_filtered_words = []
        fashion_keywords = ["apparel", "garment", "dress", "outfit", "formalwear", "casualwear","cloth","fashion","festival"]
        for i in filtered_words:
            try:
                if any(google_model.similarity(keyword, i) > 0.2 for keyword in fashion_keywords):
                    # fashion_filtered_words.append(i)
                    count+=1
            except Exception as e:
                pass

        if count > 0:
            count = 0
        else:
            count = 0
            
        # if len(fashion_filtered_words) == 0:   
            return redirect(url_for('prompt'))
        #--------------------------------------------------------------------------------------------------------
        print('2:'+filtered_words[0])
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--window-position=-2400,-2400")

        driver = webdriver.Chrome(options = options)

        final_str = ''
        colors = random.choice(current_user.info.color_preference.split(','))
        print('db:',colors)
        for color in filtered_words:
            try:
                if google_model.similarity('color',color ) > 0.3:
                    print(color)
                    colors = color 
                    break
                else:
                    continue
            except Exception as e:
                pass
        seas = seasons(current_month)
        print('sea60:',seas)
        for sea in filtered_words:
            try:
                if google_model.similarity('season',sea ) > 0.3:
                    seas = sea
                    break
                else:
                    continue
            except Exception as e:
                pass
        for fil_word in filtered_words:
            final_str += fil_word+"+"



        print(colors)
        print(seas)
        print('3:'+filtered_words[0])
        show = 'show_result'
        print(final_str)

        
        print("1:",seasons(current_month))
        driver.get(f'https://www.google.com/search?q={final_str[:-1]}+{colors}+wareable+for+{seas}+for+{current_user.info.gender}+size+{current_user.info.body_type}&sca_esv=cc6d6b10f485ae1c&rlz=1C1ONGR_enIN1090IN1092&biw=1396&bih=705&tbm=shop&sxsrf=ADLYWIKppFDlP9x0s9zSp0ISNeniOOxcZg%3A1728639281214&ei=MfEIZ6KlDNyNvr0Py5uV6Ak&ved=0ahUKEwjigbSSg4aJAxXchq8BHctNBZ0Q4dUDCAg&uact=5&oq={final_str[:-1]}&gs_lp=Egtwcm9kdWN0cy1jYyIaYmxhY2sgc2hpcnQgZm9yIG1lbiBmb3JtYWwyBBAjGCcyBhAAGAgYHjIGEAAYCBgeMgYQABgIGB5IzC5Qrw1YqiRwAHgAkAEAmAGNAqAB7RGqAQYwLjEwLjK4AQPIAQD4AQGYAgSgApQGwgIFEAAYgATCAgYQABgHGB7CAgcQABiABBgNwgIIEAAYBxgIGB7CAgsQABjWBRgIGA0YHpgDAIgGAZIHBTAuMy4xoAeoOQ&sclient=products-cc')
        # driver.get(f'https://www.google.com/search?q={show}+{style}+{cloth}+for+{gender}+{occasion}&sca_esv=cc6d6b10f485ae1c&rlz=1C1ONGR_enIN1090IN1092&biw=1396&bih=705&tbm=shop&sxsrf=ADLYWIKppFDlP9x0s9zSp0ISNeniOOxcZg%3A1728639281214&ei=MfEIZ6KlDNyNvr0Py5uV6Ak&ved=0ahUKEwjigbSSg4aJAxXchq8BHctNBZ0Q4dUDCAg&uact=5&oq=black+shirt+for+men+formal&gs_lp=Egtwcm9kdWN0cy1jYyIaYmxhY2sgc2hpcnQgZm9yIG1lbiBmb3JtYWwyBBAjGCcyBhAAGAgYHjIGEAAYCBgeMgYQABgIGB5IzC5Qrw1YqiRwAHgAkAEAmAGNAqAB7RGqAQYwLjEwLjK4AQPIAQD4AQGYAgSgApQGwgIFEAAYgATCAgYQABgHGB7CAgcQABiABBgNwgIIEAAYBxgIGB7CAgsQABjWBRgIGA0YHpgDAIgGAZIHBTAuMy4xoAeoOQ&sclient=products-cc')

        final_str = ''
        filtered_words = []
        colors = ""


        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'i0X6df'))
            )
        except Exception as e:
            print(f"Error loading elements: {e}")
            driver.quit()

        try:

            elems = driver.find_elements(By.CLASS_NAME, 'i0X6df')
        except:
            err = 1
            return render_template('prompt.html',title = 'Prompt', form = form , err = err)



        with open(f"fashion/results/{show}.html","w", encoding = 'utf-8') as f:
            for i in range(9):
                elem = elems[i]
                html = elem.get_attribute('outerHTML')
                f.write(html+"\n")

        # time.sleep(5)
        driver.close()

        

        with open(f"fashion/results/{show}.html","r+") as html_file:
            soup = BeautifulSoup(html_file, 'lxml')
            html_file.write("")

        images = soup.find_all('div', class_ = "ArOc1c")
        for image in images:
            img_link = image.img['src']
          
            img_links.append(img_link)

        titles = soup.find_all('div', class_ = "EI11Pd")
        for title in titles:
            text = title.h3.text
          
            names.append(text)

        prices = soup.find_all('span', class_ = "a8Pemb OFFNJ")
        for price in prices:
            rate = price.text
           
            rates.append(rate[3:])

        visits = soup.find_all('a', class_ = "Lq5OHe")
        for visit in visits:
            visit_url = visit['href']
           
            pro_url.append('http://www.google.com'+visit_url)

        # print(count)
        render_template("result.html")
        return redirect(url_for('result'))
    return render_template('prompt.html',title = 'Prompt', form = form, err = err)




@app.route("/result", methods = ['GET','POST'])
@login_required
def result():
    # add_item_name = []
    img = img_links

    discription = names

    price = ['₹ '+rate for rate in rates ]

    visit = pro_url

    return render_template('result.html', img= img, discription = discription, price = price ,visit= visit)



@app.route("/temp")
@login_required
def temp():

    return render_template("temp.html")


@app.route("/inventory")
@login_required
def inventory():
    category_list = []
    if Category.query.filter_by(user_id=current_user.info.user_id).first():
        categories = Category.query.filter_by(user_id=current_user.info.user_id).all()
        # print("categories")
        if type(categories) != str:
            for i in categories:
                category_list.append(i.cat_name)
        else:
            category_list.append(categories.cat_name)
    else:
        categories = ['one','two','three','four']
    return render_template("inventory.html", categories = category_list) #[categories if type(categories) == type("ghd") else name.cat_name for name in categories])

@app.route("/items")
@login_required
def items():
    item_name = []
    item_img = []
    item_price = []
    item_visit = []
    list1 = []
    if request.args.get('cat_cardId'):
        cat_cardId = request.args.get('cat_cardId')
        category_Id = Category.query.filter_by(user_id = current_user.info.id).all()
        categories = category_Id[int(cat_cardId)]
        print(categories)
        
        category_item_mixed =[item_info.name for item_info in Item.query.filter_by(user_id = current_user.info.user_id,category_id = categories.id ).all()]
        print(category_item_mixed)
        for category in category_item_mixed:
            list1 = category.split('*|*')
            item_name.append(list1[0])
            item_img.append(list1[1])
            item_price.append(list1[2])
            item_visit.append(list1[3])
    return render_template('items.html', img= item_img, discription = item_name, price = item_price ,visit= item_visit)


@app.route("/virtualtry")
@login_required
def virtualtry():

    return render_template("virtualtry.html")


@app.route("/additem",methods =['GET','POST'])
def additem():
    add_item_name = []
    if request.args.get('cardId'):
        att =  request.args.get('cardId')

        for word in names[int(att)].split():
            print(word)
            try:
                if google_model.similarity('cloth',word ) > 0.15:
                    print("True....")
                    add_item_name.append(word)
                # else:
                #     return jsonify({"success": False})
            except Exception as e:
                print(e)
        print(add_item_name[-1])
        # -----------------------------------------
        category_name = add_item_name[-1]
        item_name = f"{names[int(att)]}*|*{img_links[int(att)]}*|*{rates[int(att)]}*|*{pro_url[int(att)]}"
# def add_item_to_category(user_id, category_name, item_name):
        try:
            # Check if the category already exists for the given user
            category = Category.query.filter_by(user_id=current_user.info.user_id, cat_name=category_name).first()

            if category:
                # If category exists, use its ID
                category_id = category.id
            else:
                # If category doesn't exist, create it and add to the database
                new_category = Category(user_id=current_user.info.user_id, cat_name=category_name)
                db.session.add(new_category)
                db.session.commit()  # Commit to generate the new category ID
                category_id = new_category.id

            # Now, add the item to the Item table under the appropriate category
            new_item = Item(user_id=current_user.info.user_id, category_id=category_id, name=item_name)
            db.session.add(new_item)
            db.session.commit()

            print(f"Item '{item_name}' added to category '{category_name}'.")

        except Exception as e:
            db.session.rollback()
            print(f"An error occurred: {e}")


        # ------------------------------------------
    return jsonify({"success": True})




@app.route("/removeitem", methods=['POST'])
def removeitem():
    try:
        # Get the cardInfo from the form data
        card_info = request.form.get('cardInfo')
        if not card_info:
            return jsonify({"success": False, "error": "Missing card information."})

        # Extract details from cardInfo
        details = card_info.split('*|*')
        item_name = details[0]
        print('101:',item_name)
        # image_path = details[1]
        # price = details[2]
        # visit_url = details[3]

        # Determine the category based on the item's name
        remove_item_name = []
        for word in item_name.split():
            try:
                if google_model.similarity('cloth', word) > 0.15:
                    remove_item_name.append(word)
            except Exception as e:
                print(f"Error with word similarity: {e}")

        if not remove_item_name:
            return jsonify({"success": False, "error": "Could not determine category."})

        category_name = remove_item_name[-1]
        print('102:',category_name)
        # Remove the item from the database
        category = Category.query.filter_by(user_id=current_user.info.user_id, cat_name=category_name).first()
        if not category:
            return jsonify({"success": False, "error": "Category not found."})

        item = Item.query.filter_by(
            user_id=current_user.info.user_id,
            category_id=category.id,
            name=card_info
        ).first()



        if not item:
            return jsonify({"success": False, "error": "Item not found in the database."})

        db.session.delete(item)
        if not Item.query.filter_by(user_id=current_user.info.user_id,category_id=category.id,name=card_info).first():
            db.session.delete(category)
        db.session.commit()

        print(f"Item '{item_name}' removed from category '{category_name}'.")
        return jsonify({"success": True})

    except Exception as e:
        db.session.rollback()
        print(f"An error occurred: {e}")
        return jsonify({"success": False, "error": str(e)})

