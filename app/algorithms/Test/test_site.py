import pytest

company_phone_local = ['Apple', 'Xiaomi', 'Samsung', 'POCO', 'HONOR', 'Realme', 'Huawei', 'TCL', 'Vivo', 'Infinix', 'TECNO']


class Test:
    def test_logo(self, soup):
        logo_site = soup.select_one('#logo path').get('d').strip()
        with open('logo_svg.txt', 'r+', encoding='utf-8') as logo_local_file:
            logo_local = logo_local_file.read()
            assert logo_site == logo_local, 'Логотип сайта не совпадает!'
            print('\nПроверка логотипов пройдена')

    @pytest.mark.parametrize('select_and_telephone', [
        pytest.param(('.phone__short span', '210'), id='.phone__short span, 210'),
        pytest.param(('.phone__number', '+375 29 545-00-00'), id='.phone__number, +375 29 545-00-00')
    ])
    def test_contacts(self, soup, select_and_telephone):
        select, telephone_local = select_and_telephone
        telephone_site = soup.select(select)[0].text.strip()
        assert telephone_site == telephone_local, 'Номер телефона не совпадает!'
        print('\nПроверка номера телефона пройдена')

    def test_amount_company(self, soup):
        company_phone_site = list()
        company_phone_site.extend(sel.text.strip() for sel in soup.select('.col-lg-4.col-md-6.b10'))
        assert len(company_phone_site) == len(company_phone_local), 'Количество компаний не совпадает!'
        for elem_site, elem_local in zip(company_phone_site, company_phone_local):
            assert elem_site == elem_local, 'Порядок названий компаний нарушен!'
        print('\nПроверка названий компаний смартфонов пройдена')
