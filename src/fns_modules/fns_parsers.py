from abc import ABC, abstractmethod
import os
from typing import Any

from src.models.other_models import *
from src.models.database_models import *
from src.fns_modules.fns_misc import *
from src.fns_modules.fns_errors import NoFileToDelete



class Tag_parser_Base(ABC):
    _database_model_name: str
    def handle(self,
               elements: etree._Element, ) -> dict[str, str | list[Any]] | None:
        output = []
        tablename = self._tablename
        if tablename is None:
            print('tablename is not found.')
            return None
        for element in elements:
            if element.tag == 'Документ':
                self.org_info = self._org_info

                if self.org_info is None: continue

                if self.org_info is None:
                    print('Database model is not found.')
                    continue

                self._parse_recursive(element=element)
                element.clear()
                output.append(self.org_info)
        output = {'tablename': tablename, 'data': output}
        return output
        ...

    @property
    @abstractmethod
    def _org_info(self, ) -> dict | list | None:
        # return dict_from_database_model_name[self._database_model_name]
        ...

    @property
    @abstractmethod
    def _tablename(self, ) -> str | None:
        # return tablename_from_database_model_name[self._database_model_name]
        ...

    @abstractmethod
    def _parse_recursive(self,
                         element: etree._Element, ):
        ...




class Tag_parser_OGRN_MAIN_INFO(Tag_parser_Base):
    def __init__(self):
        self._database_model_name = 'fns_main_info_shadow'

    @property
    def _org_info(self, ) -> dict | None:
        # return dict_from_database_model_name['fns_main_info_shadow']
        return create_dict_from_database_model(fns_main_info_shadow)
        ...

    @property
    def _tablename(self, ) -> str | None:
        # return tablename_from_database_model_name['fns_main_info_shadow']
        return get_tablename_from_database_model(fns_main_info_shadow)
        ...
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
            self.org_info['inn'] = int(element.get('ИННФЛ'))
            self.org_info['ogrn'] = int(element.get('ОГРНИП'))
            for child_element in element:
                self._parse_recursive(element=child_element)

        elif element.tag == 'ФИОИП':
            self.org_info['full_name'] = (str(element.get('Фамилия')) + ' '
                                       + str(element.get('Имя')) + ' '
                                       + str(element.get('Отчество')).strip())

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
            self.org_info['inn'] = int(element.get('ИННЮЛ'))
            self.org_info['ogrn'] = int(element.get('ОГРН'))

        # # Добавить позже
        # elif element.tag == 'СвЛиценз':
        #     pass


class Tag_parser_ADDITIONAL_OKVEDS(Tag_parser_Base):
    def __init__(self):
        self._database_model_name = 'okveds_shadow'

    def handle(self,
               elements: etree._Element, ) -> dict[str, str | list[Any]] | None:
        output = []
        tablename = self._tablename

        if not tablename: return None
        self.inn, self.ogrn = (None, None)
        for element in elements:
            if self._initialize_inn_ogrn(element=element):
                self.org_info = self._org_info
                self._parse_recursive(element=element)
                output += self.org_info
            element.clear()
        output = {'tablename': tablename, 'data': output}
        return output

    @property
    def _org_info(self, ) -> dict | list:
        return []

    @property
    def _tablename(self, ) -> str | None:
        # return get_tablename_from_database_model(okveds_shadow)
        return get_tablename_from_database_model(okveds_shadow)

    def _initialize_inn_ogrn(self,
                             element, ) -> bool:
        """
        Инициилизирует self.inn, self.ogrn.
        :param element:
        :return:
        """
        if element.tag == 'Документ':
            for child_element in element:
                self._initialize_inn_ogrn(element=child_element)
                if self.ogrn and self.inn:
                    return True
        elif element.tag == 'ИПВклМСП':
            self.inn, self.ogrn = int(element.get('ИННФЛ')), int(element.get('ОГРНИП'))
            return True
        elif element.tag == 'ОргВклМСП':
            self.inn, self.ogrn = int(element.get('ИННЮЛ')), int(element.get('ОГРН'))
            return True
        return False
        ...


    def _parse_recursive(self,
                         element: etree._Element, ):
        if element.tag == 'Документ':
            for child_element in element:
                self._parse_recursive(element=child_element)
            # element.clear()
        elif element.tag == 'СвОКВЭД':
            for child_element in element:
                self._parse_recursive(element=child_element)
        elif element.tag == 'СвОКВЭДДоп':
            additional_okveds = create_dict_from_database_model(okveds_shadow)
            additional_okveds['inn'] = self.inn
            additional_okveds['ogrn'] = self.ogrn
            # additional_okveds['name'] = element.get('НаимОКВЭД')
            additional_okveds['code'] = element.get('КодОКВЭД')
            self.org_info.append(additional_okveds)



class Tag_parser_SNO_UL(Tag_parser_Base):
    def __init__(self):
        self._database_model_name = 'sno_shadow'
    @property
    def _org_info(self, ) -> dict | list | None:
        return create_dict_from_database_model(sno_shadow)

    @property
    def _tablename(self, ) -> str | None:
        return get_tablename_from_database_model(sno_shadow)


    def _parse_recursive(self,
                         element: etree._Element, ):
        if element.tag == 'Документ':
            for item in element:
                self._parse_recursive(element=item)
            element.clear()

        if element.tag == 'СведНП':
            self.org_info['inn'] = int(element.get('ИННЮЛ'))
        elif element.tag == 'СведСНР':
            self.org_info['eshn'] = True if element.get('ПризнЕСХН') == '1' else False

            self.org_info['usn'] = True if element.get('ПризнУСН') == '1' else False

            self.org_info['ausn'] = True if element.get('ПризнАУСН') == '1' else False

            self.org_info['srp'] = True if element.get('ПризнСРП') == '1' else False


class Tag_parser_SNO_IP(Tag_parser_Base):
    def __init__(self):
        self._database_model_name = 'sno_shadow'
    @property
    def _org_info(self, ) -> dict | list | None:
        return create_dict_from_database_model(sno_shadow)


    @property
    def _tablename(self, ) -> str | None:
        return get_tablename_from_database_model(sno_shadow)


    def _parse_recursive(self,
                         element: etree._Element, ):
        if element.tag == 'Документ':
            for item in element:
                self._parse_recursive(element=item)

        elif element.tag == 'СведНП':
            self.org_info['inn'] = int(element.get('ИННФЛ'))
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
    unzipper: Unzipper
    reader: File_reader
    tag_parser: Tag_parser_Base

    def parse(self,
              file_dir: str | Path,
              left: int = 0,
              right: int = 0, ) -> Generator:
        return self._parse(file_dir=file_dir,
                           left=left,
                           right=right)
        ...


    def _parse(self,
               file_dir: str | Path,
               left: int = 0,
               right: int = 0, ) -> Generator:

        file_dir = file_dir if isinstance(file_dir, Path) else Path(file_dir)

        if str(file_dir).endswith('.zip'):
            # files = self.unzipper.unzip_file(file_dir=file_dir, unzip_dir=unzip_dir, left=left, right=right)
            files = self.unzipper.unzip_data(file_dir=file_dir, left=left, right=right)

        elif str(file_dir).endswith('.xml'):
            files = [self.unzipper.unzip_data(file_dir=file_dir)]

        else:
            print(f'Unsupported file format "{file_dir}"')
            return None

        for file_data in files:
            output = self._parse_xml(file_data=file_data,)
            yield output


    def _parse_xml(self,
                   file_data: etree._Element, ) ->  dict[str, str | list[Any]] | None:
        output = self.tag_parser.handle(elements=file_data)
        file_data.clear()
        return output
        # try:
        #     elements = self.reader.get_file_root(file_dir=file_dir)
        #     output = self.tag_parser.handle(elements=elements)
        # finally:
        #     try:
        #         if delete_after_parsing is True:
        #             os.remove(file_dir)
        #     except:
        #         raise NoFileToDelete(file_dir=file_dir)
        # return output
        ...



class Parser_RSMP_MAIN_INFO(Parser_Base):
    def __init__(self, ):
        self.unzipper = Unzipper()
        self.reader = File_reader()
        self.tag_parser = Tag_parser_OGRN_MAIN_INFO()
        super().__init__()


class Parser_RSMP_ADDITIONAL_OKVEDS(Parser_Base):
    def __init__(self):
        self.unzipper = Unzipper()
        self.reader = File_reader()
        self.tag_parser = Tag_parser_ADDITIONAL_OKVEDS()
        super().__init__()
        

class Parser_SNO_UL(Parser_Base):
    def __init__(self):
        self.unzipper = Unzipper()
        self.reader = File_reader()
        self.tag_parser = Tag_parser_SNO_UL()
        super().__init__()


class Parser_SNO_IP(Parser_Base):
    def __init__(self):
        self.unzipper = Unzipper()
        self.reader = File_reader()
        self.tag_parser = Tag_parser_SNO_IP()
        super().__init__()






if __name__ == '__main__':

    def _test_parser_RSMP():
        parser_rsmp_main_info = Parser_RSMP_MAIN_INFO()
        output = parser_rsmp_main_info.parse(
            file_dir=r'E:\PycharmProjects\MegaParsers\src\downloaded_dir\data-10082026-structure-12052026.zip', left=1,
            right=0)
        if output is None: print('Err')
        else:
            result = 0
            for item in output:

                result += len(item['data'])
            print(result)


    def _test_parser_okveds():
        parser_rsmp_additional_okveds = Parser_RSMP_ADDITIONAL_OKVEDS()
        output = parser_rsmp_additional_okveds.parse(
            file_dir=r'E:\PycharmProjects\MegaParsers\src\downloaded_dir\data-10082026-structure-12052026.zip', left=1,
            right=0)
        if output is None: print('Err')
        else:
            for item in output:
                print(len(item['data']))


    def _test_parser_sno_ul():
        parser_snrul = Parser_SNO_UL()
        output = parser_snrul.parse(
            file_dir=r'E:\PycharmProjects\MegaParsers\src\downloaded_dir\data-20260625-structure-20230425.zip', left=1,
            right=3)
        if output is None: print('Err')
        else:
            for item in output:
                print(item)


    def _test_parser_sno_ip():
        parser_snrul = Parser_SNO_IP()
        output = parser_snrul.parse(
            file_dir=r'E:\PycharmProjects\MegaParsers\src\downloaded_dir\data-20260625-structure-20241025.zip', left=1,
            right=3)
        if output is None: print('Err')
        else:
            for item in output:
                print(item)
                ...


    # _test_parser_RSMP()
    _test_parser_okveds()
    # _test_parser_sno_ul()
    # _test_parser_sno_ip()
    ...