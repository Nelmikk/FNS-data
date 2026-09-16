import time
import requests
import math

from typing import Callable
from functools import wraps
from bs4 import BeautifulSoup
from seleniumbase import Driver, SB
from datetime import datetime, timedelta


all_case_types = {'A': 'Административные',
                  'G': 'Гражданские',
                  'B': 'Банкротные'
                  }

all_courts = {'VS': 'Верховный суд РФ',
              'VAS': 'Высший Арбитражный Суд РФ',
              'FASVVO': 'АС Волго-Вятского округа',
              'FASVSO': 'АС Восточно-Сибирского округа',
              'FASDVO': 'АС Дальневосточного округа',
              'FASZSO': 'АС Западно-Сибирского округа',
              'FASMO': 'АС Московского округа',
              'FASPO': 'АС Поволжского округа',
              'FASSZO': 'АС Северо-Западного округа',
              'FASSKO': 'АС Северо-Кавказского округа',
              'FASUO': 'АС Уральского округа',
              'FASCO': 'АС Центрального округа',
              '1AAS': '1 арбитражный апелляционный суд',
              '2AAS': '2 арбитражный апелляционный суд',
              '3AAS': '3 арбитражный апелляционный суд',
              '4AAS': '4 арбитражный апелляционный суд',
              '5AAS': '5 арбитражный апелляционный суд',
              '6AAS': '6 арбитражный апелляционный суд',
              '7AAS': '7 арбитражный апелляционный суд',
              '8AAS': '8 арбитражный апелляционный суд',
              '9AAS': '9 арбитражный апелляционный суд',
              '10AAS': '10 арбитражный апелляционный суд',
              '11AAS': '11 арбитражный апелляционный суд',
              '12AAS': '12 арбитражный апелляционный суд',
              '13AAS': '13 арбитражный апелляционный суд',
              '14AAS': '14 арбитражный апелляционный суд',
              '15AAS': '15 арбитражный апелляционный суд',
              '16AAS': '16 арбитражный апелляционный суд',
              '17AAS': '17 арбитражный апелляционный суд',
              '18AAS': '18 арбитражный апелляционный суд',
              '19AAS': '19 арбитражный апелляционный суд',
              '20AAS': '20 арбитражный апелляционный суд',
              '21AAS': '21 арбитражный апелляционный суд',
              'ALTAI-KRAI': 'АС Алтайского края',
              'AMURAS': 'АС Амурской области',
              'ARHANGELSK': 'АС Архангельской области',
              'ASTRAHAN': 'АС Астраханской области',
              'BELGOROD': 'АС Белгородской области',
              'BRYANSK': 'АС Брянской области',
              'VLADIMIR': 'АС Владимирской области',
              'VOLGOGRAD': 'АС Волгоградской области',
              'VOLOGDA': 'АС Вологодской области',
              'VORONEJ': 'АС Воронежской области',
              'MSK': ' АС города Москвы',
              'SPB': 'АС города Санкт-Петербурга и Ленинградской области',
              'SEVASTOPOL': 'АС города Севастополя',
              'DNR': 'АС Донецкой Народной Республики',
              'EAO': 'АС Еврейской автономной области',
              'CHITA': 'АС Забайкальского края',
              'ZAPOROZHYE': 'АС Запорожской области',
              'IVANOVO': 'АС Ивановской области',
              'IRKUTSK': 'АС Иркутской области',
              'ASKB': 'АС Кабардино-Балкарской Республики',
              'KALININGRAD': 'АС Калининградской области',
              'KALUGA': 'АС Калужской области',
              'KAMCHATKA': 'АС Камчатского края',
              'ASKCHR': 'АС Карачаево-Черкесской Республики',
              'KEMEROVO': 'АС Кемеровской области',
              'KIROV': 'АС Кемеровской области',
              'KOMI-PERM': 'АС Коми-Пермяцкого АО',
              'KOSTROMA': 'АС Костромской области',
              'KRASNODAR': 'АС Краснодарского края',
              'KRANSOYARSK': 'АС Красноярского края',
              'KURGAN': 'АС Курганской области',
              'KURSK': 'АС Курской области',
              'LIPETSK': 'АС Липецкой области',
              'LNR': 'АС Луганской Народной Республики',
              'MAGADAN': 'АС Магаданской области',
              'ASMO': 'АС Московской области',
              'MURMANSK': 'АС Мурманской области',
              'NNOV': 'АС Нижегородской области',
              'NOVGOROD': 'АС Новгородской области',
              'NOVOSIB': 'АС Новосибирской области',
              'OMSK': 'АС Омской области',
              'ORENBURG': 'АС Оренбургской области',
              'OREL': 'АС Орловской области',
              'PENZA': 'АС Пензенской области',
              'PERM': 'АС Пермского края',
              'PRIMKRAY': 'АС Приморского края',
              'PSKOV': 'АС Псковской области',
              'ADYG': 'АС Республики Адыгея',
              'ALTAI': 'АС Республики Алтай',
              'UFA': 'АС Республики Башкортостан',
              'BURYATIA': 'АС Республики Бурятия',
              'MAHACHKALA': 'АС Республики Дагестан',
              'INGUSHETIA': 'АС Республики Ингушетия',
              'KALMYK': 'АС Республики Калмыкия',
              'KARELIA': 'АС Республики Карелия',
              'KOMI': 'АС Республики Коми',
              'KRYM': 'АС Республики Крым',
              'MARI-EL': 'АС Республики Марий Эл',
              'ASRM': 'АС Республики Мордовия',
              'YAKUTSK': 'АС Республики Саха',
              'ALANIA': 'АС Республики Северная Осетия',
              'TATARSTAN': 'АС Республики Татарстан',
              'TYVA': 'АС Республики Тыва',
              'KHAKASIA': 'АС Республики Хакасия',
              'ROSTOV': 'АС Ростовской области',
              'RYAZAN': 'АС Рязанской области',
              'SAMARA': 'АС Самарской области',
              'SARATOV': 'АС Саратовской области',
              'SAKHALIN': 'АС Сахалинской области',
              'EKATERINBURG': 'АС Свердловской области',
              'SMOLENSK': 'АС Смоленской области',
              'STAVROPOL': 'АС Ставропольского края',
              'TAMBOV': 'АС Тамбовской области',
              'TVER': 'АС Тверской области',
              'TOMSK': 'АС Томской области',
              'TULA': 'АС Тульской области',
              'TUMEN': 'АС Тюменской области',
              'UDMURTIYA': 'АС Удмуртской Республики',
              'ULYANOVSK': 'АС Ульяновской области',
              'KHABAROVSK': 'АС Хабаровского края',
              'HMAO': 'АС Ханты-Мансийского АО',
              'KHERSON': 'АС Херсонской области',
              'CHEL': 'АС Челябинской области',
              'CHECHNYA': 'АС Чеченской Республики',
              'CHUVASHIA': 'АС Чувашской Республики',
              'CHUKOTKA': 'АС Чукотского АО',
              'YAMAL': 'АС Ямало-Ненецкого АО',
              'YAROSLAVL': 'АС Ярославской области',
              'KUDIMKAR': 'ПСП Арбитражного суда Пермского края',
              'NARYANMAR': 'ПСП Арбитражный суд Архангельской области',
              'SIP': 'Суд по интеллектуальным правам',
}



class Cookie_generator:
    def __generate_cookies(self,
                           ) -> dict:
        """
        Генерация кукиз для запросов в kadarbitr.
        :return:
        """
        with SB(headless=True, uc=True) as browser:
            browser.open('https://kad.arbitr.ru/')
            browser.switch_to_window(0)
            time.sleep(5)
            if browser.find_elements('a[class*="notification-popup-close"]'):
                browser.click('a[class*="notification-popup-close"]')
            time.sleep(5)
            browser.click('button[alt="Найти"]')
            time.sleep(5)   # Заменить на поиск дел, для подтверждения, что страница загрузилась полностью
            cookies = {'cookie': '; '.join(cookie['name']+'='+cookie['value'] for cookie in browser.get_cookies())}
            return cookies

    def __call__(self, *args, **kwargs):
        return self.__generate_cookies()


def ensure_cookies(func: Callable,
                   ):
    @wraps(func)
    def wrapper(*wargs,
                **kwargs,
                ) -> tuple:
        """
        Проверяет код ответа, если 200, то возвращает без изменений.
        Если 451 - содает кукиз в новой сессии.
        Если 429 - возвращает 0, тк это временная блокировка.

        Возвращает
        :param wargs:
        :param kwargs:
        :return:
        """
        num_of_tries = 0
        while num_of_tries < 3:
            response = func(*wargs, **kwargs)
            if response.status_code == 200:
                return response, kwargs['cookies']
            elif response.status_code == 451:
                print(f'451 - Фикс кукизами')
                kwargs['cookies'] = cookie_generator()
            elif response.status_code == 429:
                print(f'429 - Фикс ожиданием')
                return 0, kwargs['cookies']
            else:
                print(f'\n--------------------------\n'
                      f'{response.status_code = }\n{response.text = }'
                      f'\n--------------------------\n')
            num_of_tries += 1
        return 0, kwargs['cookies']
    return wrapper


cookie_generator = Cookie_generator()


class Parser_by_day:
    def __init__(self,
                 ):
        self.__kadarbitr_search_url = 'https://kad.arbitr.ru/Kad/SearchInstances'
        self.__cookies = cookie_generator()
        self.__kadarbitr_cases = []
        self.__kadarbitr_plaintiffs = []
        self.__kadarbitr_respondents = []
        self.__court = ''


    @ensure_cookies
    def __get_data(self,
                   date: str = datetime.strftime(datetime.today(), '%Y-%m-%d'),
                   court: str = '',
                   page: int = 1,
                   cookies: dict = {},
                   ) -> requests.models.Response:
        """
        Отправляет пост запрос, получает страницу данные по кейсам, исходя из пейлоада.
        :return:
        """
        payload = self.__create_payload(date, court, page)
        print(f'\n{payload = }\n')
        response = requests.post(self.__kadarbitr_search_url,
                                 json=payload,
                                 headers=cookies)
        return response


    def __create_payload(self,
                         date: str = datetime.strftime(datetime.today(), '%Y-%m-%d'),
                         court: str = '',
                         page: int = 1,
                         case_type: str = '',
                         ) -> dict:
        """
        Создание пейлоада для пост запроса.
        :param case_type:
        :param date:
        :param court:
        :param page:
        :return:
        """
        if case_type:                   # Если есть кейстайп, то создается чутка другой словарь
            return {'CaseNumbers': [],
                    'CaseType': case_type,
                    'Count': 25,
                    'Courts': [court],
                    'DateFrom': f"{date}T00:00:00",
                    'DateTo': f"{date}T23:59:59",
                    'Judges': [],
                    'Page': page,
                    'Sides': [],
                    'WithVKSInstances': False}
        return {'CaseNumbers': [],
                'Count': 25,
                'Courts': [court],
                'DateFrom': f"{date}T00:00:00",
                'DateTo': f"{date}T23:59:59",
                'Judges': [],
                'Page': page,
                'Sides': [],
                'WithVKSInstances': False}


    def __parse(self,
                ):
        """
        Парсит суды по всем датам.
        :return:
        """
        self.date = datetime.strptime('02.02.2020', '%d.%m.%Y') # Заменить на 01.01.2000
        all_courts_keys = [i for i in all_courts.keys()]
        all_case_types_keys = [i for i in all_case_types.keys()]
        while self.date != datetime.today():
            date_str = self.date.strftime('%Y-%m-%d')
            time_start = time.perf_counter()
            for self.__court in all_courts_keys:
                response, self.__cookies = self.__get_data(date=date_str,
                                                           court=self.__court,
                                                           cookies=self.__cookies)
                if isinstance(response, requests.models.Response):
                    case_quantity, pages = self.__get_case_quantity(response.text)
                    if case_quantity > 1000:
                        print('Кейсов больше 1к до применения доп фильтров')
                        for case_type in all_case_types_keys:
                            response, self.__cookies = self.__get_data(date=date_str,
                                                                       court=self.__court,
                                                                       cookies=self.__cookies)
                            if isinstance(response, requests.models.Response):
                                case_quantity, pages = self.__get_case_quantity(response.text)
                                if case_quantity > 1000:
                                    print('Кейсов больше 1к после применения доп фильтров')
                                    self.__parse_exact_date(date=date_str,
                                                            court=self.__court,
                                                            pages=pages,
                                                            case_type=case_type)
                                else:
                                    self.__parse_exact_date(date=date_str,
                                                            court=self.__court,
                                                            pages=pages,
                                                            case_type=case_type)  # Надо бы найти еще фильтры для кейсов

                    else:
                        self.__parse_exact_date(date=date_str,
                                                court=self.__court,
                                                pages=pages)
                else:
                    print('response не Response')
                    return
                time.sleep(6)
            self.date = self.date + timedelta(days=1)
            time_end = time.perf_counter()
            print(f'{time_end - time_start = }\n')
        pass


    def __parse_exact_date(self,
                           date: str = datetime.strftime(datetime.today(), '%Y-%m-%d'),
                           court: str = '',
                           pages: int = 1,
                           case_type: str = '',
                           ):
        """
        Парсит все страницы, используя получаемые параметры
        :param case_type:
        :param date:
        :param court:
        :param pages:
        :return:
        """
        # print(f'{pages = }')
        for page in range(1, pages+1):
            response, self.__cookies = self.__get_data(date=date,
                                                       court=self.__court,
                                                       page=page,
                                                       cookies=self.__cookies)
            if response:
                self.__parse_html(html=response.text)
                print(f'{self.__kadarbitr_cases = }')
                print(f'{self.__kadarbitr_plaintiffs = }')
                print(f'{self.__kadarbitr_respondents = }')
                if self.__kadarbitr_cases:
                    super_user.insert_many(table='kadarbitr_cases',
                                           params=self.__kadarbitr_cases)
                if self.__kadarbitr_plaintiffs:
                    super_user.insert_many(table='kadarbitr_plaintiffs',
                                           params=self.__kadarbitr_plaintiffs)
                if self.__kadarbitr_respondents:
                    super_user.insert_many(table='kadarbitr_respondents',
                                           params=self.__kadarbitr_respondents)
                self.__kadarbitr_cases = []
                self.__kadarbitr_plaintiffs = []
                self.__kadarbitr_respondents = []
            time.sleep(6)


    @staticmethod
    def __get_case_quantity(html: str,
                            ) -> tuple:
        """
        Возвращает количество кейсов и страниц.
        :param html:
        :return:
        """
        soup = BeautifulSoup(html, 'html.parser')
        case_quantity = soup.find('input', {'id': 'documentsTotalCount'}).get('value')
        try:
            case_quantity = int(case_quantity)
        except:
            case_quantity = 0
        pages = math.ceil(case_quantity / 25)
        return case_quantity, pages



    def __parse_html(self,
                     html: str,
                     ):
        """
        Парсит html-код страницы и получает основную инфу по кейсам.
        :param html:
        :return:
        """
        soup = BeautifulSoup(html, 'html.parser')
        # print(f'{soup.prettify() = }')
        date_for_case_type = datetime.strftime(self.date, '%d.%m.%Y')
        for case in soup.find_all('tr'):
            judge = case_num = case_link =\
                respondent_name = respondent_inn = \
                respondent_info = plaintiff_name = plaintiff_inn = plaintiff_info = case_type = None

            if case.find('div', {'title': all_courts[self.__court]}):
                case_date = self.date.isoformat()
                case_type = case.find('div', {'title': f'{date_for_case_type} 0:00:00'}).get('class')[0]
                court = case.find('div', {'title': all_courts[self.__court]}).text

                if case.find('div', {'class': 'judge'}):
                    judge = case.find('div', {'class': 'judge'}).get('title')

                if case.find('a', {'class': 'num_case'}):
                    case_num = case.find('a', {'class': 'num_case'}).get_text().strip()

                if case.find('a', {'class': 'num_case'}):
                    case_link = case.find('a', {'class': 'num_case'}).get('href')

                for plaintiff in case.find('td', {'class': 'plaintiff'}).find_all('span', {'class': 'js-rolloverHtml'}):
                    if plaintiff.find('strong'):
                        plaintiff_name = plaintiff.find('strong').text
                    if plaintiff.find('br'):
                        if plaintiff.find('br').next:
                            plaintiff_info = plaintiff.find('br').next.strip()
                    if plaintiff.find('div'):
                        plaintiff_inn = plaintiff.find('div').text.strip().replace('ИНН: ', '')
                    self.__kadarbitr_plaintiffs.append((case_num, plaintiff_inn, plaintiff_name, plaintiff_info))
                    plaintiff_name = plaintiff_inn = plaintiff_info = None
                for respondent in case.find('td', {'class': 'respondent'}).find_all('span', {'class': 'js-rolloverHtml'}):
                    if respondent.find('strong'):
                        respondent_name = respondent.find('strong').text
                    if respondent.find('br'):
                        if respondent.find('br').next:
                            respondent_info = respondent.find('br').next.strip()
                    if respondent.find('div'):
                        respondent_inn = respondent.find('div').text.strip().replace('ИНН: ', '')
                    self.__kadarbitr_respondents.append((case_num, respondent_inn, respondent_name, respondent_info))
                    respondent_name = respondent_inn = respondent_info = None

                # try:
                #     respondent_name = case.find('td', {'class': 'respondent'}).find('span').find('span').find('strong').text
                # except:
                #     pass
                # try:
                #     respondent_inn = case.find('td', {'class': 'respondent'}).find('span').find('div').text.strip().replace('ИНН: ', '')
                # except:
                #     pass
                # try:
                #     respondent_info = case.find('td', {'class': 'respondent'}).find('span').find('br').next.strip()
                # except:
                #     pass
                # try:
                #     plaintiff_name = case.find('td', {'class': 'plaintiff'}).find('span').find('span').find('strong').text
                # except:
                #     pass
                # try:
                #     plaintiff_inn = case.find('td', {'class': 'plaintiff'}).find('span').find('div').text.strip().replace('ИНН: ', '')
                # except:
                #     pass
                # try:
                #     plaintiff_info = case.find('td', {'class': 'plaintiff'}).find('span').find('br').next.strip()
                # except:
                #     pass
                # new_kadarbitr_data = (
                #     case_num,
                #     case_link,
                #     case_date,
                #     case_type,
                #     court,
                #     judge,
                # )
                # print(new_kadarbitr_data)
                self.__kadarbitr_cases.append((case_num,
                                               case_link,
                                               case_date,
                                               case_type,
                                               court,
                                               judge,))


    def __call__(self, *args, **kwargs):
        self.__parse()
        ...


class Parser_by_case:
    def __init__(self,
                 ):
        self.__null_cases_url = select_user.get_null_status_cases()
        self.__driver = Driver(uc=True, headless=False)
        self.__plaintiffs_data = []
        self.__data_to_update = []


    def __parse(self,
                ):
        if self.__null_cases_url:
            parsed_quantity = 0
            for url in self.__null_cases_url:
                self.__parse_url(url=url)
                parsed_quantity += 1
                if parsed_quantity == 5:
                    parsed_quantity = 0
                    print(self.__data_to_update)
                    super_user.update_many(table='kadarbitr_cases',
                                           params=self.__data_to_update,
                                           update_rows=['case_status',
                                                        'case_type',
                                                        'last_doc_name'],
                                           check_rows='case_link')
                time.sleep(5)


    def __parse_url(self,
                    url: str,
                    ):
        """
        Открывает страницу по юрл и парсит 2 строчки с нее, пиздец =)))
        :param url:
        :return:
        """
        self.__driver.open(url)
        self.__driver.switch_to_window(0)
        tries = 0
        while not self.__driver.find_elements('span[class="js-case-header-case_num"]'):
            time.sleep(1)
            if tries >= 20:
                print(f'Ошибка - {self.__class__.__name__} - {url = } - Долгое ожидание загрузки страницы')
                return
        # soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        case_status = self.__get_case_status()
        case_type = self.__get_case_type()
        last_doc_name = self.__get_last_doc_name()
        self.__data_to_update.append((case_status, case_type, last_doc_name, url))

    def __get_case_status(self,
                        ) -> str:
        case_status = self.__driver.get_text('div[class="b-case-header-desc"]')
        return case_status

    def __get_last_doc_name(self,
                            ) -> str | None:
        try:
            last_doc_name = self.__driver.get_text('h2[class="b-case-result"]')
            return last_doc_name
        except:
            return None

    def __get_case_type(self,
                        ) -> str:
        case_type = self.__driver.get_text('dt[class="b-iblock__header b-iblock__header_card"]')
        return case_type

    def __call__(self, ):
        self.__parse()
