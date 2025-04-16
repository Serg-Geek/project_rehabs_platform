from django.core.management.base import BaseCommand
from core.models import Region, City
from django.utils.text import slugify
import uuid

class Command(BaseCommand):
    help = 'Загружает начальные данные с регионами и городами России'

    def handle(self, *args, **options):
        # Список регионов и их столиц
        regions_data = [
            # Центральный федеральный округ
            {'name': 'Москва', 'capital': 'Москва'},
            {'name': 'Московская область', 'capital': 'Красногорск'},
            {'name': 'Белгородская область', 'capital': 'Белгород'},
            {'name': 'Брянская область', 'capital': 'Брянск'},
            {'name': 'Владимирская область', 'capital': 'Владимир'},
            {'name': 'Воронежская область', 'capital': 'Воронеж'},
            {'name': 'Ивановская область', 'capital': 'Иваново'},
            {'name': 'Калужская область', 'capital': 'Калуга'},
            {'name': 'Костромская область', 'capital': 'Кострома'},
            {'name': 'Курская область', 'capital': 'Курск'},
            {'name': 'Липецкая область', 'capital': 'Липецк'},
            {'name': 'Орловская область', 'capital': 'Орёл'},
            {'name': 'Рязанская область', 'capital': 'Рязань'},
            {'name': 'Смоленская область', 'capital': 'Смоленск'},
            {'name': 'Тамбовская область', 'capital': 'Тамбов'},
            {'name': 'Тверская область', 'capital': 'Тверь'},
            {'name': 'Тульская область', 'capital': 'Тула'},
            {'name': 'Ярославская область', 'capital': 'Ярославль'},
            
            # Северо-Западный федеральный округ
            {'name': 'Санкт-Петербург', 'capital': 'Санкт-Петербург'},
            {'name': 'Ленинградская область', 'capital': 'Санкт-Петербург'},
            {'name': 'Архангельская область', 'capital': 'Архангельск'},
            {'name': 'Вологодская область', 'capital': 'Вологда'},
            {'name': 'Калининградская область', 'capital': 'Калининград'},
            {'name': 'Республика Карелия', 'capital': 'Петрозаводск'},
            {'name': 'Республика Коми', 'capital': 'Сыктывкар'},
            {'name': 'Мурманская область', 'capital': 'Мурманск'},
            {'name': 'Ненецкий автономный округ', 'capital': 'Нарьян-Мар'},
            {'name': 'Новгородская область', 'capital': 'Великий Новгород'},
            {'name': 'Псковская область', 'capital': 'Псков'},
            
            # Южный федеральный округ
            {'name': 'Республика Адыгея', 'capital': 'Майкоп'},
            {'name': 'Республика Калмыкия', 'capital': 'Элиста'},
            {'name': 'Краснодарский край', 'capital': 'Краснодар'},
            {'name': 'Астраханская область', 'capital': 'Астрахань'},
            {'name': 'Волгоградская область', 'capital': 'Волгоград'},
            {'name': 'Ростовская область', 'capital': 'Ростов-на-Дону'},
            
            # Северо-Кавказский федеральный округ
            {'name': 'Республика Дагестан', 'capital': 'Махачкала'},
            {'name': 'Республика Ингушетия', 'capital': 'Магас'},
            {'name': 'Кабардино-Балкарская Республика', 'capital': 'Нальчик'},
            {'name': 'Карачаево-Черкесская Республика', 'capital': 'Черкесск'},
            {'name': 'Республика Северная Осетия — Алания', 'capital': 'Владикавказ'},
            {'name': 'Чеченская Республика', 'capital': 'Грозный'},
            {'name': 'Ставропольский край', 'capital': 'Ставрополь'},
            
            # Приволжский федеральный округ
            {'name': 'Республика Башкортостан', 'capital': 'Уфа'},
            {'name': 'Республика Марий Эл', 'capital': 'Йошкар-Ола'},
            {'name': 'Республика Мордовия', 'capital': 'Саранск'},
            {'name': 'Республика Татарстан', 'capital': 'Казань'},
            {'name': 'Удмуртская Республика', 'capital': 'Ижевск'},
            {'name': 'Чувашская Республика', 'capital': 'Чебоксары'},
            {'name': 'Кировская область', 'capital': 'Киров'},
            {'name': 'Нижегородская область', 'capital': 'Нижний Новгород'},
            {'name': 'Оренбургская область', 'capital': 'Оренбург'},
            {'name': 'Пензенская область', 'capital': 'Пенза'},
            {'name': 'Пермский край', 'capital': 'Пермь'},
            {'name': 'Самарская область', 'capital': 'Самара'},
            {'name': 'Саратовская область', 'capital': 'Саратов'},
            {'name': 'Ульяновская область', 'capital': 'Ульяновск'}
        ]

        # Создаем регионы и их столицы
        for region_data in regions_data:
            region_name = region_data['name']
            capital_name = region_data['capital']
            
            # Генерируем уникальный slug для региона
            base_slug = slugify(region_name)
            region_slug = f"{base_slug}-{str(uuid.uuid4())[:8]}"
            capital_slug = slugify(capital_name)
            
            # Создаем или получаем регион
            region, created = Region.objects.get_or_create(
                name=region_name,
                defaults={'slug': region_slug}
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Создан регион: {region_name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Регион уже существует: {region_name}'))

            # Создаем столицу региона
            city, created = City.objects.get_or_create(
                region=region,
                name=capital_name,
                defaults={'slug': capital_slug}
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Создана столица: {capital_name} ({region_name})'))
            else:
                self.stdout.write(self.style.WARNING(f'Столица уже существует: {capital_name} ({region_name})'))

        self.stdout.write(self.style.SUCCESS('Загрузка регионов и их столиц завершена')) 