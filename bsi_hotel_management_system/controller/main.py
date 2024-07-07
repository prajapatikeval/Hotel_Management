from odoo import http
from odoo.http import request
from odoo import fields as _
from odoo.exceptions import ValidationError, AccessDenied
from datetime import datetime




class AuthenticationController(http.Controller):

    # @http.route('/web/login', type="http", auth="none")
    # def web_login(self, redirect=None, **kwargs):
    #     if http.request.env.user.id:
    #         return http.request.redirect(redirect or '/web')
    #     else:
    #         return http.request.redirect('/login')


    # Register Route
    @http.route('/register',type="http", auth="public", website=True)
    def register(self, **kwargs):

        if http.request.httprequest.method == 'POST':
            name = kwargs.get('name')
            email = kwargs.get('email')
            password = kwargs.get('password')
            phone = kwargs.get('phone')
            address = kwargs.get('address')
            confirm_password = kwargs.get('confirm_password')

            existing_user = http.request.env['res.users'].sudo().search([('login','=',email)])

            if existing_user:
                return http.request.render('bsi_hotel_management_system.bsi_register_page_id',{'error':'User Already exists'})

            if password != confirm_password:
                return http.request.render('bsi_hotel_management_system.bsi_register_page_id',{'error':'Password does not match'})
            
            

            group_portal, group_user = http.request.env.ref('base.group_portal'), http.request.env.ref('base.group_user')
            custom_group_user = http.request.env.ref('bsi_hotel_management_system.group_hotel_user')
            # Creating a new user
            user_vals = {
                'name': name,
                'login': email,
                'email': email,
                'phone': phone,
                'street': address,
                'password': password,
                'company_id': http.request.env.company.id,
                'groups_id':[ (4, group_portal.id),(4, custom_group_user.id) ,(3, group_user.id) ]
            }

            http.request.env['res.users'].sudo().create(user_vals)
            
            return http.request.redirect('/login')
        
        else:
            return http.request.render('bsi_hotel_management_system.bsi_register_page_id',{})

    # Login Route
    @http.route('/login', type="http",auth="public", website=True)
    def login(self,*args, **kwargs):

        if http.request.httprequest.method == 'POST':
            login = kwargs.get('email')
            password = kwargs.get('password')

            try:
                user = http.request.session.authenticate(
                    db = http.request.session.db,
                    login = login,
                    password = password,
                )
                if user:
                    return http.request.redirect('/')
            except Exception as e:
                return http.request.render('bsi_hotel_management_system.bsi_login_page_id',{'error':'invalid username or password'})
        else:
            return http.request.render('bsi_hotel_management_system.bsi_login_page_id',{})

    @http.route('/logout', type="http",auth="user", website=True)
    def logout(self, **kwargs):
        http.request.session.logout()
        return http.request.redirect('/')


# Simple Pages
class Mypage(http.Controller):
    
    # Home
    @http.route('/', type="http", auth="public", website=True)
    def my_webpage(self):
        return http.request.render('bsi_hotel_management_system.bsi_home_page_id', {})
    
    
    @http.route('/send_mail', type="http", auth="public", website=True)
    def send_mail_homepage(self, **kwargs):
        user = http.request.env.user
        email = kwargs.get('email')
        if email:
            message = f'''Thank You for connnecting with us! <br/> <b>The Leela</b>'''

            vals = {
                'subject': 'We have received your response on our website',
                'body_html': message,
                'email_from': 'admin@yourcompany.example.com',
                'email_to': email,
                'auto_delete': False,
            }

            mail_id = http.request.env['mail.mail'].sudo().create(vals)
            mail_id.sudo().send()

        return http.request.render('bsi_hotel_management_system.bsi_home_page_id',{})



    # About Page
    @http.route('/about', type="http", auth="public", website=True)
    def about_us(self, **kwargs):
        return http.request.render('bsi_hotel_management_system.bsi_about_us_id', {})


    # Contact Page
    @http.route('/contact', type="http", auth="public", website=True)
    def contact_us(self, **kwargs):
        user = http.request.env.user

        if http.request.httprequest.method == 'POST':
            success = True
            error = "Message Sent Succesfully!"

            try:
                name = kwargs.get('name')
                email = kwargs.get('email')
                message = kwargs.get('message')

                message = f'''Message From: <b>{name}</b> <br/> 
                            Email Id: <b>{email}</b> <br/><br/>
                            &nbsp; {message}'''

                vals = {
                    'subject': 'Contact Message',
                    'body_html': message,
                    'email_from': email,
                    'email_to': 'kevalprajapati1001@gmail.com',
                    'auto_delete': False,
                }

                mail_id = http.request.env['mail.mail'].sudo().create(vals)
                mail_id.sudo().send()


            except Exception as e:
                success = False
                error = e

            return http.request.render('bsi_hotel_management_system.bsi_contact_us_id', {'success':success,'error':error})
        
        return http.request.render('bsi_hotel_management_system.bsi_contact_us_id', {})
    
    # Contact Page
    @http.route('/profile', type="http", auth="user", website=True)
    def user_profile(self, **kwargs):
        user = http.request.env.user
        if http.request.httprequest.method == 'POST':
            user.write(kwargs)
            return http.request.render('bsi_hotel_management_system.bsi_user_profile_id',{'user':user,"message":'Profile Updated Successfully!'})
        return http.request.render('bsi_hotel_management_system.bsi_user_profile_id', {'user':user})
    
    # change password page
    @http.route('/change_password', type="http", auth="user", website=True)
    def change_password(self, **kwargs):
        user = http.request.env.user

        if http.request.httprequest.method == 'POST':
            success = True
            error = "Password Changed Sucessfully!"

            old_password = kwargs.get('old_password')
            new_password = kwargs.get('new_password')
            confirm_password = kwargs.get('confirm_password')
            

            if new_password != confirm_password:
                success = False
                error = "Password and Confirm Password does not match"
            else:
                try:
                    http.request.env['res.users'].change_password(old_password, new_password)
                    new_token = http.request.env.user._compute_session_token(http.request.session.sid)
                    http.request.session.session_token = new_token
                except AccessDenied as e:
                    error = 'Incorrect Current Password!'
                    success = False

            return http.request.render('bsi_hotel_management_system.bsi_change_password_page_id',{'success':success,'error':error})
        return http.request.render('bsi_hotel_management_system.bsi_change_password_page_id',{})

    
    @http.route('/send_otp', type="http", auth="public", website=True)
    def send_otp(self, user):
        
        user.generate_otp()
        
        http.request.env.ref('bsi_hotel_management_system.send_otp_template').send_mail(user.id, force_send=True)
        
        message = "OTP sent!"
        http.request.session['message'] = message
        http.request.session['email'] = user.login
        return http.request.redirect('/forgot_password')

    @http.route('/check_email', type="http", auth="public", website=True)
    def check_email(self, **kwargs):
        error = None
        message = None 

        if http.request.httprequest.method == 'POST':
            email = kwargs.get('email')
            user = http.request.env['res.users'].sudo().search([('login','=',email)])
            if user:
                error = None
                message = "OTP sent!"
                self.send_otp(user)
                
                return http.request.redirect('/forgot_password')
            else:
                error = "Email Id Does Not exist" 
                return http.request.render('bsi_hotel_management_system.bsi_check_email_page_id',{'error':error})
                
        return http.request.render('bsi_hotel_management_system.bsi_check_email_page_id',{'error':error,'message':message})

    
    @http.route('/forgot_password', type="http", auth="public", website=True)
    def forgot_password(self, **kwargs):

        error = None
        message = http.request.session.pop('message', None)
        email =  http.request.session.pop('email', None)

        if http.request.httprequest.method == 'POST':
            otp = kwargs.get('otp_field')
            email = kwargs.get('email')
            user = http.request.env['res.users'].sudo().search([('login','=',email)]) 

            if user.random_otp == int(otp):
                http.request.session['email'] = user.login
                return http.request.redirect('/create_password')
            else:
                error = "OTP does not match"

        return http.request.render('bsi_hotel_management_system.bsi_forgot_password_page_id',{'email':email,'error':error,'message':message})
        

    @http.route('/create_password', type="http", auth="public", website=True)
    def create_password(self, **kwargs):
        
        if http.request.httprequest.method == 'POST':
            success = True
            error = "Password Changed Sucessfully!"
            email =  http.request.session.pop('email', None)
            user = http.request.env['res.users'].sudo().search([('login','=',email)])
        
            new_password = kwargs.get('new_password')
            confirm_password = kwargs.get('confirm_password')

            if new_password != confirm_password:
                success = False
                error = "Password and Confirm Password does not match"
            else:
                print(f"{user.login, user}".center(150,'-'))
                user.sudo().write({'password': new_password})

            return http.request.render('bsi_hotel_management_system.bsi_create_password_page_id',{'success':success,'error':error})
                    
        return http.request.render('bsi_hotel_management_system.bsi_create_password_page_id',{})

    # Check Booking Credentials
    

    # Creating a booking Using JS
    @http.route('/create/booking',  type="json", methods=['POST'], auth="user",csrf=False, website=True)
    def create_booking(self,room_id,**kwargs):
        user = request.env.user
        data = request.env['room.type'].browse(room_id)
        # Getting data from js
        name = kwargs.get('name')
        phone = kwargs.get('phone')
        address = kwargs.get('street')
        email = kwargs.get('email')
        country = kwargs.get('country')
        state = kwargs.get('state')
        check_in = kwargs.get('date-in')
        check_out = kwargs.get('date-out')

        formatted_check_in = datetime.strptime(check_in,'%d %B, %Y')
        formatted_check_out = datetime.strptime(check_out,'%d %B, %Y')

        num_rooms = kwargs.get('room')
        room_type = request.env['room.type'].browse(int(room_id))


        if room_type.check_room_availablity(check_in, check_out, int(num_rooms)):
            
            existing_booking_detail = request.env['booking.detail'].sudo().search([('email','=',user.email)],limit=1)

            if existing_booking_detail and existing_booking_detail.status == "confirm":
                if existing_booking_detail.check_in != formatted_check_in and existing_booking_detail.check_out != formatted_check_out:
                    
                    vals = []
                    vals.append((0,0,{
                        'room_id':room_id,
                        'price':data.room_price,
                        'discount':data.offer,
                        'num_of_rooms':num_rooms,
                        'adult':data.max_adult,
                        'child':data.max_child,
                    }))

                    booking = request.env['booking.detail'].create({
                        'booking_detail_ids':vals,
                        'user_id':user.id,
                        'guest_name':name,
                        'email':email,
                        'phone':phone,
                        'address':address,
                        'country':country,
                        'state':state,
                        'status':'confirm',
                        'check_in': formatted_check_in,
                        'check_out': formatted_check_out,
                    })
                    request.env.ref('bsi_hotel_management_system.send_booking_status_template').send_mail(booking.id, force_send=True)
                else:
                    rooms = [i for i in existing_booking_detail.booking_detail_ids.room_id]
                    bookings = [i for i in existing_booking_detail.booking_detail_ids]
                    
                    if room_type in rooms:
                        for booking in bookings:
                            if booking.room_id in rooms:
                                booking.num_of_rooms += int(num_rooms)
                    else:
                        request.env['booking.detail.line'].sudo().create({
                            'booking_id':existing_booking_detail.id,
                            'num_of_rooms':num_rooms,
                            'room_id':room_id,
                        })
                        request.env.ref('bsi_hotel_management_system.send_booking_status_template').send_mail(existing_booking_detail.id, force_send=True)

            else:
                print(f"Else".center(150,'-'))
                print(f"{room_id}".center(150,'-'))
                print(f"{data.room_price}".center(150,'-'))
                print(f"{data.offer}".center(150,'-'))
                print(f"{data}".center(150,'-'))
                print(f"Else".center(150,'-'))
                vals = []
                vals.append((0,0,{
                    'room_id':room_id,
                    'price':data.room_price,
                    'discount':data.offer,
                    'num_of_rooms':num_rooms,
                    'adult':data.max_adult,
                    'child':data.max_child,
                }))
                print(f"{vals}".center(150,'-'))

                booking = request.env['booking.detail'].create({
                    'booking_detail_ids':vals,
                    'user_id':user.id,
                    'guest_name':name,
                    'email':email,
                    'phone':phone,
                    'address':address,
                    'country':country,
                    'state':state,
                    'status':'confirm',
                    'check_in': formatted_check_in,
                    'check_out': formatted_check_out,
                })
                request.env.ref('bsi_hotel_management_system.send_booking_status_template').send_mail(booking.id, force_send=True)
            room_type.update_room_status(int(num_rooms),state = 'confirm', user_id = name)
        else:
            available = False
            message = "Not Enough rooms"


    # register page for booking
    @http.route('/booking/<int:room_id>', type="http", auth="user", website=True)
    def booking(self,room_id, **kwargs):

        user = http.request.env.user
        data = http.request.env['room.type'].browse(room_id)

        if http.request.httprequest.method == 'POST':
            name = kwargs.get('name')
            phone = kwargs.get('phone')
            address = kwargs.get('street')
            email = kwargs.get('email')
            country = kwargs.get('country')
            state = kwargs.get('state')

            check_in = kwargs.get('date-in')
            check_out = kwargs.get('date-out')


            formatted_check_in = datetime.strptime(check_in,'%d %B, %Y')
            formatted_check_out = datetime.strptime(check_out,'%d %B, %Y')

            num_rooms = kwargs.get('room')
            room_type = http.request.env['room.type'].browse(int(room_id))

            
            if room_type.check_room_availablity(check_in, check_out, int(num_rooms)):
                available = True
                message = "Booked Room Successfully!"
                
                existing_booking_detail = http.request.env['booking.detail'].sudo().search([('email','=',user.email)],limit=1)

                if existing_booking_detail and existing_booking_detail.status == "confirm":
                    if existing_booking_detail.check_in != formatted_check_in and existing_booking_detail.check_out != formatted_check_out:
                        
                        vals = []
                        vals.append((0,0,{
                            'room_id':room_id,
                            'price':data.room_price,
                            'discount':data.offer,
                            'num_of_rooms':num_rooms,
                            'adult':data.max_adult,
                            'child':data.max_child,
                        }))

                        booking = http.request.env['booking.detail'].create({
                            'booking_detail_ids':vals,
                            'user_id':user.id,
                            'guest_name':name,
                            'email':email,
                            'phone':phone,
                            'address':address,
                            'country':country,
                            'state':state,
                            'status':'confirm',
                            'check_in': formatted_check_in,
                            'check_out': formatted_check_out,
                        })
                        http.request.env.ref('bsi_hotel_management_system.send_booking_status_template').send_mail(booking.id, force_send=True)
                    else:
                        # rooms = [i for i in existing_booking_detail.booking_detail_ids.room_id]
                        # bookings = [i for i in existing_booking_detail.booking_detail_ids]
                        
                        # if room_type in rooms:
                        #     for booking in bookings:
                        #         print(f"{booking}".center(150,'-'))
                        #         if booking.room_id in rooms:
                        #             print(f"{booking}".center(150,'-'))
                        #             booking.num_of_rooms += int(num_rooms)
                        # else:
                        http.request.env['booking.detail.line'].sudo().create({
                            'booking_id':existing_booking_detail.id,
                            'num_of_rooms':num_rooms,
                            'room_id':room_id,
                        })
                        http.request.env.ref('bsi_hotel_management_system.send_booking_status_template').send_mail(existing_booking_detail.id, force_send=True)

                else:
                    vals = []
                    vals.append((0,0,{
                        'room_id':room_id,
                        'price':data.room_price,
                        'discount':data.offer,
                        'num_of_rooms':num_rooms,
                        'adult':data.max_adult,
                        'child':data.max_child,
                    }))

                    booking = http.request.env['booking.detail'].create({
                        'booking_detail_ids':vals,
                        'user_id':user.id,
                        'guest_name':name,
                        'email':email,
                        'phone':phone,
                        'address':address,
                        'country':country,
                        'state':state,
                        'status':'confirm',
                        'check_in': formatted_check_in,
                        'check_out': formatted_check_out,
                    })
                    http.request.env.ref('bsi_hotel_management_system.send_booking_status_template').send_mail(booking.id, force_send=True)
                room_type.update_room_status(int(num_rooms),state = 'confirm', user_id = name)
            else:
                available = False
                message = "Not Enough rooms"

            return http.request.render('bsi_hotel_management_system.bsi_booking_id', {'user':user,'data':data,'available':available,'message':message})

            
        return http.request.render('bsi_hotel_management_system.bsi_booking_id', {'user':user,'data':data})

    @http.route('/my_bookings', type="http", auth="public", website=True)
    def my_bookings(self):
        user = http.request.env.user
        delete_message = http.request.session.pop('delete_message', None)
        my_booking = http.request.env['booking.detail'].sudo().search([('user_id', '=', user.id)])

        return http.request.render('bsi_hotel_management_system.bsi_bookings_id', {'user':user, 'my_booking':my_booking,'delete_message':delete_message})

    @http.route('/my_booking_detail/<int:booking_id>', type="http", auth="public", website=True)
    def my_booking_detail(self, booking_id):
        data = http.request.env['booking.detail'].browse(booking_id)
        invoice_id = http.request.env['room.invoices'].search([('booking_order_id','=',booking_id)],limit=1)

        return http.request.render('bsi_hotel_management_system.bsi_my_booking_detail_page_id', {'data':data, 'invoice_id':invoice_id})


    # Creating a booking
    @http.route('/cancel/booking/<int:booking_id>', type="http", auth="user", website=True)
    def cancel_booking(self,booking_id,**kwargs):
        booking_detail_line = http.request.env['booking.detail.line'].sudo().browse(booking_id)
        booking_detail = booking_detail_line.booking_id
        room_id = booking_detail_line.room_id
        
        booking_detail_line.unlink()
        room_id.update_room_status(1,state="checkout")

        message = "Booking Cancelled!"
        http.request.session['delete_message'] = message

        total_lines = 0
        for line in booking_detail.booking_detail_ids:
            total_lines += 1
        
        if total_lines == 0:
            booking_detail.unlink()
            return http.request.redirect("my_bookings") 

        return http.request.redirect("my_booking_detail/%s" %booking_detail.id)
    
    @http.route('/cancel/booking_detail/<int:booking_detail_id>', type="http", auth="user", website=True)
    def cancel_booking_detail(self,booking_detail_id,**kwargs):
        booking_detail = http.request.env['booking.detail'].sudo().browse(booking_detail_id)
        room_id = booking_detail.booking_detail_ids.room_id
        
        booking_detail.unlink()
        room_id.update_room_status(1,state="checkout")

        message = "Booking Cancelled!"
        http.request.session['delete_message'] = message

        return http.request.redirect("my_bookings")
    

    # Rooms Page
    @http.route('/rooms', type="http", auth='public', website=True)
    def rooms(self, **kwargs):
        datas = http.request.env['room.type'].search([], order="available_rooms desc")
        
        return http.request.render(
            'bsi_hotel_management_system.bsi_rooms_page_id',{'datas': datas}
        )

    # Check booking using JS
    @http.route('/check_booking', type="json", methods=['POST'], auth="public",csrf=False, website=True)
    def check_booking(self,room_id, **kwargs):
        
        check_in_date = kwargs.get('date-in')
        check_out_date = kwargs.get('date-out')
        num_rooms = kwargs.get('room')
        room_type = http.request.env['room.type'].browse(int(room_id))

        if check_in_date and check_out_date:
            if room_type.check_room_availablity(check_in_date, check_out_date, int(num_rooms)):
                return True
            else:
                return False
            
    # Individual Room Page
    @http.route('/room/<int:page_id>', type="http", auth="public", website=True)
    def room(self,page_id, **kwargs):

        data = http.request.env['room.type'].browse(page_id)

        return http.request.render("bsi_hotel_management_system.bsi_room_page_id",{
            'data':data
        })

    
    # Creating a review
    @http.route('/create/review', type="http", auth="user", website=True)
    def review_create(self, **post):
        room_id = int(post.get('room_id'))
        review_name = post.get('room_review_name')
        review_description = post.get('room_review_description')
        review_email = post.get('room_review_email')
        review_rate = post.get('rate')

        review_line = http.request.env['room.review.line'].sudo().create({
            'room_id':room_id
        })

        review = http.request.env['room.review'].sudo().create({
            'room_review_name':review_name,
            'room_review_description':review_description,
            'room_review_email':review_email,
            'room_review_rate':review_rate,
        })

        review_line.write({'room_review_id':review.id})

        return http.request.redirect('/room/%s' % room_id)

