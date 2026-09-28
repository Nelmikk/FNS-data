from abc import ABC, abstractmethod
from collections.abc import Callable
from copy import deepcopy

from src.models.other_models import *
from src.models.database_models import *
from src.fns_modules.fns_misc import *
from src.errors.database_errors import TableNotFound



class Init_ogrn_inn_mixin:
    def initialize(self, element: etree._Element, ):
        if element.tag == 'Документ':
            for child_element in element:
                self.initialize(element=child_element)
                if self.ogrn and self.inn:
                    return True
        elif element.tag == 'ИПВклМСП':
            self.inn, self.ogrn = str(element.get('ИННФЛ')), str(element.get('ОГРНИП'))
            return True
        elif element.tag == 'ОргВклМСП':
            self.inn, self.ogrn = str(element.get('ИННЮЛ')), str(element.get('ОГРН'))
            return True
        return False



class Tag_parser_Base(ABC):
    _database_model: type[Base_shadow_table, Base, Base_mixin]
    _pass_on_empty_data: bool = False
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
                output.append(self.org_info)
        output = Parser_output(tablename=tablename, data=output)
        # output = {'tablename': tablename, 'data': output}
        return output


    @property
    # @abstractmethod
    def _org_info(self, ) -> dict:
        return deepcopy(self._database_model.base_column_values)


    @property
    # @abstractmethod
    def _tablename(self, ) -> str | None:
        return self._database_model.__tablename__


    @abstractmethod
    def _parse_recursive(self,
                         element: etree._Element, ):
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



class Tag_parser_ADDITIONAL_OKVEDS(Tag_parser_Base, Init_ogrn_inn_mixin):
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



class Tag_parser_LICENSES(Tag_parser_Base, Init_ogrn_inn_mixin):
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
                'date': datetime.strptime(element.get('ДатаЛиценз'), '%d.%m.%Y').date().isoformat() if element.get('ДатаЛиценз') else None,
                'date_start': datetime.strptime(element.get('ДатаНачЛиценз'), '%d.%m.%Y').date().isoformat() if element.get('ДатаНачЛиценз') else None,
                'date_end': datetime.strptime(element.get('ДатаКонЛиценз'), '%d.%m.%Y').date().isoformat() if element.get('ДатаКонЛиценз') else None,
            })


class Tag_parser_SNO_UL(Tag_parser_Base):
    _database_model = sno_shadow

    # def handle(self,
    #            elements: etree._Element, ) -> Parser_output:
    #     output = []
    #     tablename = self._tablename
    #
    #     if tablename is None:
    #         raise TableNotFound(self._database_model)
    #
    #     for element in elements:
    #         if element.tag == 'Документ':
    #             self.org_info = self._org_info
    #
    #             if self.org_info is None:
    #                 print('Database model is not found.')
    #                 continue
    #
    #             self._parse_recursive(element=element)
    #             element.clear()
    #
    #             output.append(self.org_info)
    #     output = Parser_output(tablename=tablename, data=output)
    #     # output = {'tablename': tablename, 'data': output}
    #     return output


    def _parse_recursive(self,
                         element: etree._Element, ):
        if element.tag == 'Документ':
            for item in element:
                self._parse_recursive(element=item)
            # element.clear()

        if element.tag == 'СведНП':
            self.org_info['inn'] = str(element.get('ИННЮЛ'))
        elif element.tag == 'СведСНР':
            self.org_info['eshn'] = True if element.get('ПризнЕСХН') == '1' else False

            self.org_info['usn'] = True if element.get('ПризнУСН') == '1' else False

            self.org_info['ausn'] = True if element.get('ПризнАУСН') == '1' else False

            self.org_info['srp'] = True if element.get('ПризнСРП') == '1' else False


class Tag_parser_SNO_IP(Tag_parser_Base):
    _database_model = sno_shadow
    # def __init__(self, ):
    #     self._database_model = sno_shadow

    # @property
    # def _org_info(self, ) -> dict | list | None:
    #     return create_dict_from_database_model(sno_shadow)
    #
    #
    # @property
    # def _tablename(self, ) -> str | None:
    #     return get_tablename_from_database_model(sno_shadow)


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
    unzipper: Unzipper
    reader: File_reader
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
        return self._parse(file_dir=file_dir,
                           left=left,
                           right=right)



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
                   file_data: etree._Element, ) ->  Parser_output:
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




class Parser_RSMP_MAIN_INFO(Parser_Base):
    tag_parser = Tag_parser_OGRN_MAIN_INFO
    def __init__(self, ):
        # self.tag_parser = self.tag_parser()
        super().__init__()


class Parser_RSMP_ADDITIONAL_OKVEDS(Parser_Base):
    tag_parser = Tag_parser_ADDITIONAL_OKVEDS
    def __init__(self, ):
        # self.tag_parser = self.tag_parser()
        super().__init__()


class Parser_RSMP_LICENSES(Parser_Base):
    tag_parser = Tag_parser_LICENSES

    def __init__(self, ):
        # self.tag_parser = self.tag_parser()
        super().__init__()


class Parser_SNO_UL(Parser_Base):
    tag_parser = Tag_parser_SNO_UL

    def __init__(self, ):
        # self.tag_parser = self.tag_parser()
        super().__init__()


class Parser_SNO_IP(Parser_Base):
    tag_parser = Tag_parser_SNO_IP
    def __init__(self, ):
#         self.tag_parser = self.tag_parser()
        super().__init__()






if __name__ == '__main__':

    def _test_parser_RSMP():
        parser_rsmp_main_info = Parser_RSMP_MAIN_INFO()
        output = parser_rsmp_main_info.parse(
            file_dir=r'E:\PycharmProjects\MegaParsers\src\downloaded_dir\data-10082026-structure-12052026.zip', left=1,
            right=2)
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
            right=2)
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

    def _test_parser_licenses():
        parser_licenses = Parser_RSMP_LICENSES()
        output = parser_licenses.parse(
            file_dir=r'E:\PycharmProjects\MegaParsers\src\downloaded_dir\data-10082026-structure-12052026.zip', left=1,
            right=2)
        if output is None: print('Err')
        else:
            for item in output:
                print(item['data'])


    # _test_parser_RSMP()
    # _test_parser_okveds()
    # _test_parser_licenses()
    # _test_parser_sno_ul()
    # _test_parser_sno_ip()
    ...