from abc import ABC, abstractmethod
from copy import deepcopy

from src.models.other_models import *
from src.models.database_models import *
from src.fns_modules.fns_misc import *
from src.errors.database_errors import TableNotFound


class Tag_parser_Base(ABC):
    """
    Base-класс для наследования парсеров xml-файлов.
    """
    # Обязательно задается внутри класса ДО инициилизации и обязательно должен иметь ниже перечисленные родительские классы.
    _database_model: type[Base_shadow_table, Base, Base_mixin]

    def handle(self,
               elements: etree._Element, ) -> Parser_output:
        """
        Парсинг xml-файла, который передается в виде _Element.
        :param elements:
        :return:
        """
        output = []
        tablename = self._tablename

        if tablename is None:
            raise TableNotFound(self._database_model)

        for element in elements:
            if element.tag == 'Документ':
                self.org_info = self._org_info

                if self.org_info is None:
                    raise TableNotFound(self._database_model)

                self._parse_recursive(element=element)
                element.clear()
                output.append(self.org_info)
        output = Parser_output(tablename=tablename, data=output)
        return output


    @property
    def _org_info(self, ) -> dict:
        """
        Возвращает пустой словарь для заполнения, исходя из модели таблицы.
        :return:
        """
        return deepcopy(self._database_model.base_column_values)


    @property
    def _tablename(self, ) -> str | None:
        """
        Возвращает название таблицы, исходя из модели таблицы.
        :return:
        """
        return self._database_model.__tablename__


    @abstractmethod
    def _parse_recursive(self,
                         element: etree._Element, ):
        """
        Рекурсивный парсинг xml-файла.
        :param element:
        :return:
        """
        ...




class Tag_parser_OGRN_MAIN_INFO(Tag_parser_Base):
    _database_model = fns_main_info_shadow

    def _parse_recursive(self,
                         element: etree._Element, ) -> None:
        if element.tag == 'Документ':
            self.org_info['inclusion_date'] = datetime.strptime(element.get('ДатаВклМСП'), '%d.%m.%Y').date()
            self.org_info['subject_type'] = element.get('ВидСубМСП')
            self.org_info['subject_category'] = element.get('КатСубМСП')
            self.org_info['is_social'] = element.get('СведСоцПред')
            for child_element in element:
                self._parse_recursive(element=child_element)

        elif element.tag == 'ИПВклМСП':
            self.org_info['inn'] = str(element.get('ИННФЛ'))
            self.org_info['ogrn'] = str(element.get('ОГРНИП'))
            for child_element in element:
                self._parse_recursive(element=child_element)

        elif element.tag == 'ФИОИП':
            first_name = str(element.get('Фамилия'))
            surname = str(element.get('Имя'))
            patronymic = str(element.get('Отчество'))
            self.org_info['full_name'] = ((first_name if first_name is not None and first_name != 'None' else '') + ' '
                                          + (surname if surname is not None and surname != 'None' else '') + ' '
                                          + (patronymic if patronymic is not None and patronymic != 'None' else '') + ' ').strip()

        elif element.tag == 'СведМН':
            self.org_info['region_code'] = element.get('КодРегион')
            for child_element in element:
                self._parse_recursive(child_element)

        elif element.tag == 'Регион':
            self.org_info['region'] = element.get('Тип') + ' ' + element.get('Наим')

        elif element.tag == 'Район':
            self.org_info['district'] = element.get('Тип') + ' ' + element.get('Наим')

        elif element.tag == 'Город':
            self.org_info['area'] = element.get('Тип') + ' ' + element.get('Наим')

        elif element.tag == 'СвОКВЭД':
            for child_element in element:
                self._parse_recursive(child_element)

        if element.tag == 'СвОКВЭДОсн':
            self.org_info['main_okved_code'] = element.get('КодОКВЭД')
            self.org_info['main_okved_name'] = element.get('НаимОКВЭД')

        elif element.tag == 'ОргВклМСП':
            self.org_info['full_name'] = element.get('НаимОрг')
            self.org_info['short_name'] = element.get('НаимОргСокр')
            self.org_info['inn'] = str(element.get('ИННЮЛ'))
            self.org_info['ogrn'] = str(element.get('ОГРН'))



class Tag_parser_ADDITIONAL_OKVEDS(Tag_parser_Base, ):
    _database_model = okveds_shadow

    def handle(self,
               elements: etree._Element, ) -> Parser_output:
        output = []
        tablename = self._tablename

        if tablename is None:
            raise TableNotFound(self._database_model)

        for element in elements:
            if element.tag == 'Документ':
                self.org_info = self._org_info
                # print(len(self.org_info['additional_okveds_data']))

                if self.org_info is None:
                    print('Database model is not found.')
                    continue

                self._parse_recursive(element=element)
                element.clear()

                if not self.org_info['additional_okveds_data']: continue

                output.append(self.org_info)
        output = Parser_output(tablename=tablename, data=output)
        return output


    def _parse_recursive(self,
                         element: etree._Element, ):
        if element.tag == 'Документ':

            for child_element in element:
                self._parse_recursive(element=child_element)

        elif element.tag == 'ИПВклМСП':
            self.org_info['inn'] = str(element.get('ИННФЛ'))
            self.org_info['ogrn'] = str(element.get('ОГРНИП'))

        elif element.tag == 'ОргВклМСП':
            self.org_info['inn'] = str(element.get('ИННЮЛ'))
            self.org_info['ogrn'] = str(element.get('ОГРН'))

        elif element.tag == 'СвОКВЭД':
            for child_element in element:
                self._parse_recursive(element=child_element)
        elif element.tag == 'СвОКВЭДДоп':
            self.org_info['additional_okveds_data'].append({'name': element.get('НаимОКВЭД'),
                                                            'code': element.get('КодОКВЭД')})



class Tag_parser_LICENSES(Tag_parser_Base, ):
    _database_model = licenses_shadow

    def handle(self,
               elements: etree._Element, ) -> Parser_output:
        output = []
        tablename = self._tablename

        if tablename is None:
            raise TableNotFound(self._database_model)
        for element in elements:
            if element.tag == 'Документ':
                self.org_info = self._org_info

                if self.org_info is None:
                    print('Database model is not found.')
                    continue
                self._parse_recursive(element=element)
                element.clear()

                if not self.org_info['licenses_data']: continue

                output.append(self.org_info)
        output = Parser_output(tablename=tablename, data=output)
        return output


    def _parse_recursive(self,
                         element: etree._Element, ):
        if element.tag == 'Документ':

            for item in element:
                self._parse_recursive(element=item)

        elif element.tag == 'ИПВклМСП':
            self.org_info['inn'] = str(element.get('ИННФЛ'))
            self.org_info['ogrn'] = str(element.get('ОГРНИП'))

        elif element.tag == 'ОргВклМСП':
            self.org_info['inn'] = str(element.get('ИННЮЛ'))
            self.org_info['ogrn'] = str(element.get('ОГРН'))

        elif element.tag == 'СвЛиценз':
            self.org_info['licenses_data'].append({
                'num': element.get('НомЛиценз') if element.get('НомЛиценз') else None,
                'date': datetime.strptime(element.get('ДатаЛиценз'), '%d.%m.%Y').date().isoformat() if element.get('ДатаЛиценз') else None,
                'date_start': datetime.strptime(element.get('ДатаНачЛиценз'), '%d.%m.%Y').date().isoformat() if element.get('ДатаНачЛиценз') else None,
                'date_end': datetime.strptime(element.get('ДатаКонЛиценз'), '%d.%m.%Y').date().isoformat() if element.get('ДатаКонЛиценз') else None,
            })


class Tag_parser_SNO_UL(Tag_parser_Base):
    _database_model = sno_shadow

    def _parse_recursive(self,
                         element: etree._Element, ):
        if element.tag == 'Документ':
            for item in element:
                self._parse_recursive(element=item)

        if element.tag == 'СведНП':
            self.org_info['inn'] = str(element.get('ИННЮЛ'))
        elif element.tag == 'СведСНР':
            self.org_info['eshn'] = True if element.get('ПризнЕСХН') == '1' else False

            self.org_info['usn'] = True if element.get('ПризнУСН') == '1' else False

            self.org_info['ausn'] = True if element.get('ПризнАУСН') == '1' else False

            self.org_info['srp'] = True if element.get('ПризнСРП') == '1' else False


class Tag_parser_SNO_IP(Tag_parser_Base):
    _database_model = sno_shadow

    def _parse_recursive(self,
                         element: etree._Element, ):
        if element.tag == 'Документ':
            for item in element:
                self._parse_recursive(element=item)

        elif element.tag == 'СведНП':
            self.org_info['inn'] = str(element.get('ИННФЛ'))
            self.org_info['ogrn'] = str(element.get('ОГРНИП'))
        elif element.tag == 'СведСНР':
            if element.get('ПризнСНР') == '1':
                self.org_info['usn'] = True
            elif element.get('ПризнСНР') == '2':
                self.org_info['ausn'] = True
            elif element.get('ПризнСНР') == '3':
                self.org_info['eshn'] = True
            elif element.get('ПризнСНР') == '4':
                self.org_info['psn'] = True
            elif element.get('ПризнСНР') == '5':
                self.org_info['npd'] = True




class Parser_Base(ABC):
    """
    Base-класс для парсеров xml-файлов.
    """
    # Базовый у всех, задавать в классах-наследниках не надо.
    unzipper: Unzipper
    # Базовый у всех, задавать в классах-наследниках не надо.
    reader: File_reader
    # Обязательно задается у каждого отдельного класса-наследника.
    tag_parser: Tag_parser_Base

    @abstractmethod
    def __init__(self, ):
        self.tag_parser = self.tag_parser()
        self.unzipper = Unzipper()
        self.reader = File_reader()

    def parse(self,
              file_dir: str | Path,
              left: int = 0,
              right: int = 0, ) -> Generator:
        """
        Парсинг xml-файла или xml-файлов в заданных переменными left и right границах zip-архив.
            Возвращается генератор спаршенных данных.
            Если
        :param file_dir:
        :param left:
        :param right:
        :return:
        """
        file_dir = file_dir if isinstance(file_dir, Path) else Path(file_dir)

        if str(file_dir).endswith('.zip'):
            files = self.unzipper.unzip_data(file_dir=file_dir, left=left, right=right) # Генератор

        elif str(file_dir).endswith('.xml'):
            files = [self.unzipper.unzip_data(file_dir=file_dir)]                       # Массив из одного элемента
        # Если файл имеет неподдерживаемый формат, то возвращает None.
        else:
            print(f'Unsupported file format "{file_dir}"')
            return None

        for file_data in files:
            output = self._parse_xml(file_data=file_data,)
            yield output



    # def _parse(self,
    #            file_dir: str | Path,
    #            left: int = 0,
    #            right: int = 0, ) -> Generator:
    #
    #     file_dir = file_dir if isinstance(file_dir, Path) else Path(file_dir)
    #
    #     if str(file_dir).endswith('.zip'):
    #         files = self.unzipper.unzip_data(file_dir=file_dir, left=left, right=right) # Генератор
    #
    #     elif str(file_dir).endswith('.xml'):
    #         files = [self.unzipper.unzip_data(file_dir=file_dir)]                       # Массив из одного элемента
    #
    #     else:
    #         print(f'Unsupported file format "{file_dir}"')
    #         return None
    #
    #     for file_data in files:
    #         output = self._parse_xml(file_data=file_data,)
    #         yield output


    def _parse_xml(self,
                   file_data: etree._Element, ) ->  Parser_output:
        output = self.tag_parser.handle(elements=file_data)
        file_data.clear()
        return output




class Parser_RSMP_MAIN_INFO(Parser_Base):
    tag_parser = Tag_parser_OGRN_MAIN_INFO
    def __init__(self, ):
        super().__init__()


class Parser_RSMP_ADDITIONAL_OKVEDS(Parser_Base):
    tag_parser = Tag_parser_ADDITIONAL_OKVEDS
    def __init__(self, ):
        super().__init__()


class Parser_RSMP_LICENSES(Parser_Base):
    tag_parser = Tag_parser_LICENSES

    def __init__(self, ):
        super().__init__()


class Parser_SNO_UL(Parser_Base):
    tag_parser = Tag_parser_SNO_UL

    def __init__(self, ):
        super().__init__()


class Parser_SNO_IP(Parser_Base):
    tag_parser = Tag_parser_SNO_IP
    def __init__(self, ):
        super().__init__()

