from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi

#import CRUD operations
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

#set up database connection and create a session
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

class webserverHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		try:

			if self.path.endswith("/new"):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()

				output = ""
				output = "<html><body><a href = '/restaurants' >Back to Restaurants</a><br><h2>Add New Restaurant</h2>"
				output += "Enter a New Restaurant below:<br>"
				output += "<form method='POST' enctype='multipart/form-data' action='/new'><p>Enter restaurant name to add here:</p><input name='message' type='text' ><input type='submit' value='Submit'> </form>"
				output += "</body></html>"
				self.wfile.write(output)
				print(output)
				return

			if self.path.endswith("/restaurants"):
				all_restaurants = session.query(Restaurant).all()	
				output = ""
				output+= "<html><body><a href = '/new' >Enter New Restaurant</a><br>"
				output += "<h2>All Restaurants</h2><br>"

				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()

				for restaurant in all_restaurants:
					output+=restaurant.name
					output+="<br><a href='/restaurants/%s/edit'>Edit</a>"%restaurant.id
					output+="<br><a href='/restaurants/%s/delete'>Delete</a><br><br>"%restaurant.id
				output+= "</body></html>"
				self.wfile.write(output)
				print(output)
				return

			if self.path.endswith("/edit"):
				restaurant_id = self.path.split('/')[2]
				print("restaurant_id is "+restaurant_id)
				restaurantQuery = session.query(Restaurant).filter_by(id=restaurant_id).one()
				print("restaurant name is "+restaurantQuery.name)


				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()
				output = ""
				output+= "<html><body><a href = '/new' >Enter New Restaurant</a><br>"
				output += "<h2>Edit Restaurant Name</h2><br>"
				#ask user to enter new name
				output += "Enter new name for restaurant below:<br>"
				output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/edit'>"%restaurant_id
				output += "<input name = 'newRestaurantName' type='text' placeholder ='%s'>"%restaurantQuery.name
				output += "<input type='submit' value='Rename'>"
				output+= "</form>"
				output+= "</body></html>"
				self.wfile.write(output)
				print(output)
				print("X successfully got here X")
				return

			if self.path.endswith("/delete"):
				restaurant_id = self.path.split('/')[2]
				print("restaurant_id is "+restaurant_id)
				restaurantQuery = session.query(Restaurant).filter_by(id=restaurant_id).one()
				print("restaurant name is "+restaurantQuery.name)
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()
				
				output = ""
				output+= "<html><body><a href = '/new' >Enter New Restaurant</a><br>"
				output += "<h2>Delete</h2><br>"
				#ask user to enter new name
				output += "Are you sure you want to delete %s?<br>"%restaurantQuery.name
				output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/delete'>"%restaurant_id
				output += "<input type='submit' value='Delete'>"
				output+= "</form>"
				output+= "</body></html>"
				self.wfile.write(output)
				print(output)
				print("X successfully got here X")
				return

		except IOError:
			self.send_error(404, "File Not Found %s" % self.path)

	def do_POST(self):
		try:
			
			if self.path.endswith("/new"):
				ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
				if ctype == 'multipart/form-data':
					fields=cgi.parse_multipart(self.rfile, pdict)
					messagecontent = fields.get('message')
				newRestaurant = Restaurant(name = messagecontent[0])
				session.add(newRestaurant)
				session.commit()
				self.send_response(301)
				self.send_header('Content-type', 'text/html')
				self.send_header('Location', '/restaurants')
				self.end_headers()

			if self.path.endswith("/edit"):
				print("inside the POST edit function!!!!!")
				ctype, pdict = cgi.parse_header(
					self.headers.getheader('content-type'))
				print("cgi.parse worked")
				if ctype == 'multipart/form-data':
					print("inside of ctype==multipartformdata")
					fields = cgi.parse_multipart(self.rfile, pdict)
					print("parsed fields")
					print(fields)
					messagecontent = fields.get('newRestaurantName')
					print("messagecontent gotten")
					restaurant_id = self.path.split('/')[2]
					print("restaurant_id is " + restaurant_id)
					
					restaurantQuery = session.query(Restaurant).filter_by(id=restaurant_id).one()

					if restaurantQuery != []:
						restaurantQuery.name = messagecontent[0]
						session.add(restaurantQuery)
						session.commit()
						self.send_response(301)
						self.send_header('Content-type', 'text/html')
						self.send_header('Location', '/restaurants')
						self.end_headers()

			if self.path.endswith("/delete"):
				print("inside the POST delete function!!!!!")
				ctype, pdict = cgi.parse_header(
					self.headers.getheader('content-type'))
				print("cgi.parse worked")
				if ctype == 'multipart/form-data':
					print("inside of ctype==multipartformdata")
					restaurant_id = self.path.split('/')[2]
					print("restaurant_id is " + restaurant_id)
					
					restaurantQuery = session.query(Restaurant).filter_by(id=restaurant_id).one()

					if restaurantQuery != []:
						session.delete(restaurantQuery)
						session.commit()
						self.send_response(301)
						self.send_header('Content-type', 'text/html')
						self.send_header('Location', '/restaurants')
						self.end_headers()
		except:
			pass
def main():
	try:
		port = 8080
		server = HTTPServer(('',port), webserverHandler)
		print("Web server running on port %s" % port)
		server.serve_forever()

	except KeyboardInterrupt:
		print("^C entered, stopping web server...")
		server.socket.close()
if __name__ == '__main__':
	main()