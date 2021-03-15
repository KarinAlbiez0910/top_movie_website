import requests

api_key = "f8af01cad255748858e08c309f186b18"
params = {
    'api_key': api_key,
}
id= 591955
root_url = f"https://api.themoviedb.org/3/movie/{id}"
response = requests.get(root_url, params=params)
data_response = response.json()
print(data_response)
api_title = data_response['original_title']
api_year = data_response['release_date'].split('-')[0]
api_description = data_response['overview']
image_base_url = "https://image.tmdb.org/t/p/w500"
api_img_url = image_base_url + data_response['poster_path']
selected_movie = Movie(
    title=api_title,
    year= api_year,
    description=api_description,
    img_url = api_img_url
db.session.add(selected_movie)
db.session.commit()
