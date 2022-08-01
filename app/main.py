from app.settings import app, Base, engine
from app.login import login
from app.views import UserView, AdvertisementView

app.add_url_rule('/login/', methods=['POST'], view_func=login)
app.add_url_rule('/user/', methods=['POST'], view_func=UserView.as_view(name='create_user'))
app.add_url_rule('/user/<int:user_id>/', methods=['GET'], view_func=UserView.as_view(name='get_user'))
app.add_url_rule('/advertisement/', methods=['POST'], view_func=AdvertisementView.as_view(name='create_advertisement'))
app.add_url_rule(
    '/advertisement/<int:advertisement_id>/',
    methods=['GET', 'DELETE', 'PUT'],
    view_func=AdvertisementView.as_view(
        name='get_advertisement'
    ))

Base.metadata.create_all(engine)

if __name__ == '__main__':
    app.run()
