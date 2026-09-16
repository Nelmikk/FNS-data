from lxml import etree
import os
from datetime import datetime


this_dir = os.getcwd()


class Base_Parser:
    _table_name = ''

    def _parse(self,
                *args,
                **kwargs, ):
        return ''
        ...


    def _parse_recursive(self,
                          *args,
                          **kwargs, ):
        ...


    @property
    def _data_dict(self,
                   *args,
                   **kwargs, ):
        return ''


    def parse_by_path(self,
                 full_file_dir: str,
                 *args,
                 **kwargs, ) -> dict:
        root = etree.parse(fr'{full_file_dir}').getroot()
        return {self._table_name: [self._parse(item) for item in root[1:]]}
        ...



class Base_Parser_async:
    _table_name = ''

    async def _parse(self,
                     *args,
                     **kwargs, ):
        return ''
        ...

    async def _parse_recursive(self,
                               *args,
                               **kwargs, ):
        ...

    @property
    def _data_dict(self,
                   *args,
                   **kwargs, ):
        return ''

    async def parse_by_path(self,
                            full_file_dir: str,
                            *args,
                            **kwargs, ) -> dict:
        root = etree.parse(fr'{full_file_dir}').getroot()
        return {self._table_name: [await self._parse(item) for item in root[1:]]}
        ...



class Parser_RSMP(Base_Parser):
    """
    Парсит основную инфу.
    """
    def _parse(self,
               item: etree._Element, ) -> dict | tuple | None:
        self.main_info_dict, self.additional_okveds = self._data_dict
        self._parse_recursive(root=item)
        for additional_okved in self.additional_okveds:
            additional_okved['inn'] = self.main_info_dict['inn']
            additional_okved['ogrn'] = self.main_info_dict['ogrn']
        return self.main_info_dict, self.additional_okveds
        ...


    @property
    def _data_dict(self, ):
        """
        Создание пустого словаря для записи данных по организации.
        :return:
        """
        return {
            'inclusion_date': None,                                          # Дата включения в реестр МСП                                      ДатаВклМСП
            'subject_type': None,                                            # Тип субъекта (Юр лицо/ИП/тд)                                     ВидСубМСП
            'subject_category': None,                                        # Категория субъекта (Микро/малое/среднее предприятие)             КатСубМСП
            'is_social': None,                                               # Является ли субъект социальным предприятием                      СведСоцПред

            'avg_employees_num': None,                                       # Среднесписочная численность работников                           ССЧР
            'inn': None,                                                     # ИНН                                                              ИННЮЛ/ИННФЛ
            'ogrn': None,                                                    # ОГРН                                                             ОГРН/ОГРНИП
            'full_name': None ,                                              # ФИО ИП/Полное название организации                               ФИОИП
            'short_name': None,                                              # Сокращенное название организации                                 НаимОргСокр

            'region_code': None,                                             # Код региона                                                      КодРегион
            'region': None,                                                  # Субъект РФ                                                       Регион
            'district': None,                                                # Район                                                            Район
            'area': None,                                                    # Населенный пункт                                                 НаселПункт

                    # Сведения об основном ОКВЭДе                                      СвОКВЭДОсн
            'main_okved_code': None,                                         # Код ОКВЭДа                                                       КодОКВЭД
            'main_okved_name': None,                                         # Наименование ОКВЭДа                                              НаимОКВЭД
            # 'additional_okveds': [],
        }, []


    def _parse_recursive(self,
                         root: etree._Element,
                         *args,
                         **kwargs, ):
        if root.tag == 'Документ':
            self.main_info_dict['inclusion_date'] = datetime.strptime(root.get('ДатаВклМСП'), '%d.%m.%Y').date()
            self.main_info_dict['subject_type'] = root.get('ВидСубМСП')
            self.main_info_dict['subject_category'] = root.get('КатСубМСП')
            self.main_info_dict['is_social'] = root.get('СведСоцПред')
            for item in root:
                self._parse_recursive(root=item)
            root.clear()

        elif root.tag == 'ИПВклМСП':
            self.main_info_dict['inn'] = int(root.get('ИННФЛ'))
            self.main_info_dict['ogrn'] = int(root.get('ОГРНИП'))
            for item in root:
                self._parse_recursive(root=item)
                root.clear()

        elif root.tag == 'ФИОИП':
            self.main_info_dict['full_name'] = (str(root.get('Фамилия')) + ' '
                                                + str(root.get('Имя')) + ' '
                                                + str(root.get('Отчество')).strip())

        elif root.tag == 'СведМН':
            self.main_info_dict['region_code'] = root.get('КодРегион')
            for item in root:
                self._parse_recursive(root=item)
                root.clear()

        elif root.tag == 'Регион':
            self.main_info_dict['region'] = root.get('Тип') + ' ' + root.get('Наим')

        elif root.tag == 'Район':
            self.main_info_dict['district'] = root.get('Тип') + ' ' + root.get('Наим')

        elif root.tag == 'Город':
            self.main_info_dict['area'] = root.get('Тип') + ' ' + root.get('Наим')

        elif root.tag == 'СвОКВЭД':
            for item in root:
                self._parse_recursive(root=item)
            root.clear()

        if root.tag == 'СвОКВЭДОсн':
            self.main_info_dict['main_okved_code'] = root.get('КодОКВЭД')
            self.main_info_dict['main_okved_name'] = root.get('НаимОКВЭД')

        if root.tag == 'СвОКВЭДДоп':
            self.additional_okveds.append({
                'code': root.get('КодОКВЭД'),
                'name': root.get('НаимОКВЭД')
            })

        elif root.tag == 'ОргВклМСП':
            self.main_info_dict['full_name'] = root.get('НаимОрг')
            self.main_info_dict['short_name'] = root.get('НаимОргСокр')
            self.main_info_dict['inn'] = int(root.get('ИННЮЛ'))
            self.main_info_dict['ogrn'] = int(root.get('ОГРН'))

        # Добавить позже
        elif root.tag == 'СвЛиценз':
            pass


    def parse_by_path(self,
                      full_file_dir: str,
                      *args, **kwargs) -> dict:
        root = etree.parse(fr'{full_file_dir}').getroot()

        data = [self._parse(item) for item in root[1:]]

        main_info = [i[0] for i in data if i[0]]
        additional_okveds = []
        for item in data: # Этот цикл режет скорость на ~10%, пиздец
            for okved_data in item[1]:
                if okved_data: additional_okveds.append(okved_data)

        return {'fns_main_info_shadow': main_info,
                'okveds_shadow': additional_okveds,
                }


class Parser_RSMP_async(Base_Parser_async):
    """
    Парсит основную инфу.
    """
    async def _parse(self,
                     item: etree._Element, ) -> dict | tuple | None:
        self.main_info_dict, self.additional_okveds = self._data_dict
        await self._parse_recursive(root=item)
        for additional_okved in self.additional_okveds:
            additional_okved['inn'] = self.main_info_dict['inn']
            additional_okved['ogrn'] = self.main_info_dict['ogrn']

        return self.main_info_dict, self.additional_okveds
        ...


    @property
    def _data_dict(self, ):
        """
        Создание пустого словаря для записи данных по организации.
        :return:
        """
        return {
            'inclusion_date': None,                                          # Дата включения в реестр МСП                                      ДатаВклМСП
            'subject_type': None,                                            # Тип субъекта (Юр лицо/ИП/тд)                                     ВидСубМСП
            'subject_category': None,                                        # Категория субъекта (Микро/малое/среднее предприятие)             КатСубМСП
            'is_social': None,                                               # Является ли субъект социальным предприятием                      СведСоцПред

            'avg_employees_num': None,                                       # Среднесписочная численность работников                           ССЧР
            'inn': None,                                                     # ИНН                                                              ИННЮЛ/ИННФЛ
            'ogrn': None,                                                    # ОГРН                                                             ОГРН/ОГРНИП
            'full_name': None ,                                              # ФИО ИП/Полное название организации                               ФИОИП
            'short_name': None,                                              # Сокращенное название организации                                 НаимОргСокр

            'region_code': None,                                             # Код региона                                                      КодРегион
            'region': None,                                                  # Субъект РФ                                                       Регион
            'district': None,                                                # Район                                                            Район
            'area': None,                                                    # Населенный пункт                                                 НаселПункт

                    # Сведения об основном ОКВЭДе                                      СвОКВЭДОсн
            'main_okved_code': None,                                         # Код ОКВЭДа                                                       КодОКВЭД
            'main_okved_name': None,                                         # Наименование ОКВЭДа                                              НаимОКВЭД
            # 'additional_okveds': [],
        }, []


    async def _parse_recursive(self,
                               root: etree._Element,
                               *args,
                               **kwargs, ):
        if root.tag == 'Документ':
            self.main_info_dict['inclusion_date'] = datetime.strptime(root.get('ДатаВклМСП'), '%d.%m.%Y').date()
            self.main_info_dict['subject_type'] = root.get('ВидСубМСП')
            self.main_info_dict['subject_category'] = root.get('КатСубМСП')
            self.main_info_dict['is_social'] = root.get('СведСоцПред')
            for item in root:
                await self._parse_recursive(root=item)
            root.clear()

        elif root.tag == 'ИПВклМСП':
            self.main_info_dict['inn'] = int(root.get('ИННФЛ'))
            self.main_info_dict['ogrn'] = int(root.get('ОГРНИП'))
            for item in root:
                await self._parse_recursive(root=item)
                root.clear()

        elif root.tag == 'ФИОИП':
            self.main_info_dict['full_name'] = (str(root.get('Фамилия')) + ' '
                                                + str(root.get('Имя')) + ' '
                                                + str(root.get('Отчество')).strip())

        elif root.tag == 'СведМН':
            self.main_info_dict['region_code'] = root.get('КодРегион')
            for item in root:
                await self._parse_recursive(root=item)
                root.clear()

        elif root.tag == 'Регион':
            self.main_info_dict['region'] = root.get('Тип') + ' ' + root.get('Наим')

        elif root.tag == 'Район':
            self.main_info_dict['district'] = root.get('Тип') + ' ' + root.get('Наим')

        elif root.tag == 'Город':
            self.main_info_dict['area'] = root.get('Тип') + ' ' + root.get('Наим')

        elif root.tag == 'СвОКВЭД':
            for item in root:
                await self._parse_recursive(root=item)
            root.clear()

        elif root.tag == 'СвОКВЭДотч':
            for item in root:
                await self._parse_recursive(root=item)
            root.clear()

        if root.tag == 'СвОКВЭДОсн':
            self.main_info_dict['main_okved_code'] = root.get('КодОКВЭД')
            self.main_info_dict['main_okved_name'] = root.get('НаимОКВЭД')

        if root.tag == 'СвОКВЭДДоп':
            self.additional_okveds.append({
                'code': root.get('КодОКВЭД'),
                'name': root.get('НаимОКВЭД')
            })

        elif root.tag == 'ОргВклМСП':
            self.main_info_dict['full_name'] = root.get('НаимОрг')
            self.main_info_dict['short_name'] = root.get('НаимОргСокр')
            self.main_info_dict['inn'] = int(root.get('ИННЮЛ'))
            self.main_info_dict['ogrn'] = int(root.get('ОГРН'))

        # Добавить позже
        elif root.tag == 'СвЛиценз':
            pass


    async def parse_by_path(self, full_file_dir: str, *args, **kwargs) -> dict:
        root = etree.parse(fr'{full_file_dir}').getroot()

        data = [await self._parse(item) for item in root[1:]]

        main_info = [i[0] for i in data if i[0]]
        additional_okveds = []
        for item in data: # Этот цикл режет скорость на ~10%, пиздец
            for okved_data in item[1]:
                if okved_data: additional_okveds.append(okved_data)

        return {'fns_main_info_shadow': main_info, 'okveds_shadow': additional_okveds}




class Parser_SNR(Base_Parser):
    _table_name = 'sno_shadow'

    """
    Парсит СНО у ЮЛ.
    """
    def _parse(self,
               item: etree._Element, ) -> dict:
        self.sno_dict = self._data_dict
        self._parse_recursive(root=item)
        return self.sno_dict
        ...

    @property
    def _data_dict(self, ):
        """
        Создание пустого словаря для записи СНО по организации.
        :return:
        """
        return {
            'inn': None,
            'eshn': False,
            'usn': False,
            'ausn': False,
            'srp': False,
            'psn': False,
            'npd': False,
        }

    def _parse_recursive(self,
                         root: etree._Element,
                         *args,
                         **kwargs, ):
        if root.tag == 'Документ':
            for item in root:
                self._parse_recursive(root=item)
            root.clear()

        if root.tag == 'СведНП':
            self.sno_dict['inn'] = int(root.get('ИННЮЛ'))
        elif root.tag == 'СведСНР':
            if root.get('ПризнЕСХН') == '1':
                self.sno_dict['eshn'] = True
            if root.get('ПризнУСН') == '1':
                self.sno_dict['usn'] = True
            if root.get('ПризнАУСН') == '1':
                self.sno_dict['ausn'] = True
            if root.get('ПризнСРП') == '1':
                self.sno_dict['srp'] = True




class Parser_SNR_async(Base_Parser_async):
    _table_name = 'sno_shadow'

    """
    Парсит СНО у ЮЛ.
    """
    async def _parse(self,
               item: etree._Element, ) -> dict:
        self.sno_dict = self._data_dict
        await self._parse_recursive(root=item)
        return self.sno_dict
        ...

    @property
    def _data_dict(self, ):
        """
        Создание пустого словаря для записи СНО по организации.
        :return:
        """
        return {
            'inn': None,
            'eshn': False,
            'usn': False,
            'ausn': False,
            'srp': False,
            'psn': False,
            'npd': False,
        }

    async def _parse_recursive(self,
                         root: etree._Element,
                         *args,
                         **kwargs, ):
        if root.tag == 'Документ':
            for item in root:
                await self._parse_recursive(root=item)
            root.clear()

        if root.tag == 'СведНП':
            self.sno_dict['inn'] = int(root.get('ИННЮЛ'))
        elif root.tag == 'СведСНР':
            if root.get('ПризнЕСХН') == '1':
                self.sno_dict['eshn'] = True
            if root.get('ПризнУСН') == '1':
                self.sno_dict['usn'] = True
            if root.get('ПризнАУСН') == '1':
                self.sno_dict['ausn'] = True
            if root.get('ПризнСРП') == '1':
                self.sno_dict['srp'] = True




class Parser_SNRIP(Parser_SNR):
    """
    Парсит СНО у ИП.
    """
    def _parse(self,
               item: etree._Element, ) -> dict:
        self.sno_dict = self._data_dict
        self._parse_recursive(root=item)
        return self.sno_dict
        ...


    @property
    def _data_dict(self, ):
        return super()._data_dict


    def _parse_recursive(self,
                         root: etree._Element,
                         *args,
                         **kwargs, ):
        if root.tag == 'Документ':
            for item in root:
                self._parse_recursive(root=item)

        elif root.tag == 'СведНП':
            self.sno_dict['inn'] = int(root.get('ИННФЛ'))
        elif root.tag == 'СведСНР':
            if root.get('ПризнСНР') == '1':
                self.sno_dict['usn'] = True
            elif root.get('ПризнСНР') == '2':
                self.sno_dict['ausn'] = True
            elif root.get('ПризнСНР') == '3':
                self.sno_dict['eshn'] = True
            elif root.get('ПризнСНР') == '4':
                self.sno_dict['psn'] = True
            elif root.get('ПризнСНР') == '5':
                self.sno_dict['npd'] = True



class Parser_SNRIP_async(Parser_SNR_async):
    """
    Парсит СНО у ИП.
    """
    async def _parse(self,
               item: etree._Element, ) -> dict:
        self.sno_dict = self._data_dict
        await self._parse_recursive(root=item)
        return self.sno_dict
        ...


    @property
    def _data_dict(self, ):
        return super()._data_dict


    async def _parse_recursive(self,
                         root: etree._Element,
                         *args,
                         **kwargs, ):
        if root.tag == 'Документ':
            for item in root:
                await self._parse_recursive(root=item)

        elif root.tag == 'СведНП':
            self.sno_dict['inn'] = int(root.get('ИННФЛ'))
        elif root.tag == 'СведСНР':
            if root.get('ПризнСНР') == '1':
                self.sno_dict['usn'] = True
            elif root.get('ПризнСНР') == '2':
                self.sno_dict['ausn'] = True
            elif root.get('ПризнСНР') == '3':
                self.sno_dict['eshn'] = True
            elif root.get('ПризнСНР') == '4':
                self.sno_dict['psn'] = True
            elif root.get('ПризнСНР') == '5':
                self.sno_dict['npd'] = True