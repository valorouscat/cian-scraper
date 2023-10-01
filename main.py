from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import csv
from fake_useragent import UserAgent
import random


def run_playwright(playwright):
    ua = UserAgent()
    roof = [2.7, 2.5, 2.6, 2.8, 3.0]
    with open('output.csv', 'w', newline="") as file:
        fill_line = csv.writer(file)
        webkit = playwright.chromium
        browser = webkit.launch(headless=False)
        context = browser.new_context(user_agent=ua.random)
        context_map = browser.new_context(user_agent=ua.random)
        page_finder = context_map.new_page()
        page_finder.goto('https://www.addressextractor.ru/')
        page_map = context_map.new_page()
        page_map.goto('https://www.google.com/maps/dir///@54.9832415,82.8139833,12z/data=!4m2!4m1!3e2?entry=ttu')
        search_page = context.new_page()

        search_page.wait_for_timeout(100)
        for j in range(1, 15):
            search_page.goto(
                f"https://novosibirsk.cian.ru/cat.php?deal_type=sale&district%5B0%5D=215&engine_version=2&object_type%5B0%5D=1&offer_type=flat&p={j}")
            playwright.selectors.set_test_id_attribute('data-name')
            offer_card = search_page.get_by_test_id('CardComponent')
            for i in range(offer_card.count()):
                try:
                    search_page.wait_for_timeout(random.randint(100, 600))

                    with context.expect_page() as new_page_info:
                        offer_card.nth(i).click()  # Opens a new tab
                    new_page = new_page_info.value
                    new_page.wait_for_load_state()

                    if new_page.title() != search_page.title():
                        new_page.wait_for_timeout(random.randint(100,500))
                        result = [None]*8
                        result[0] = new_page.url
                        playwright.selectors.set_test_id_attribute('class')
                        address = new_page.get_by_test_id('a10a3f92e9--address--SMU25')
                        result[1] = (address.nth(address.count() - 2).text_content()+' '+address.nth(address.count() - 1).text_content())

                        info = new_page.get_by_test_id('a10a3f92e9--color_black_100--Ephi7 a10a3f92e9--lineHeight_6u--cedXD a10a3f92e9--fontWeight_bold--BbhnX a10a3f92e9--fontSize_16px--QNYmt a10a3f92e9--display_block--KYb25 a10a3f92e9--text--e4SBY')
                        result[2] = (info.first.text_content()[:-3])
                        result[3] = '0,'+str(random.randint(0, 99))

                        page_finder.get_by_test_id('address-box-widthex').fill('Новосибирск ' + result[1])
                        page_finder.get_by_test_id('address-box-widthex').press('Enter')
                        page_finder.wait_for_timeout(1000)
                        metro = page_finder.get_by_test_id('geo-item').last.text_content()
                        metro = metro[13:][:metro[13:].find('Линия')]
                        print(result[1])
                        print(metro)
                        page_map.get_by_test_id('tactile-searchbox-input').nth(0).fill(result[1])
                        page_map.wait_for_timeout(random.randint(100, 300))
                        page_map.get_by_test_id('tactile-searchbox-input').nth(1).fill(metro)
                        page_map.get_by_test_id('tactile-searchbox-input').nth(1).press('Enter')
                        result[4] = page_map.get_by_test_id('ivN21e tUEI8e fontBodyMedium').first.text_content()[:-3]
                        page_map.wait_for_timeout(random.randint(100, 350))
                        # result[3] = ('') # bus
                        # result[4] = ('') # metro
                        for count in range(1, info.count()):
                            try:
                                if len(str(int(info.nth(count).text_content()))) == 4:
                                    result[5] = (info.nth(count).text_content())
                            except ValueError:
                                pass

                        summary = new_page.get_by_test_id('a10a3f92e9--item--qJhdR')
                        for count in range(summary.count()):
                            if len(summary.nth(count).text_content()) > 15 and summary.nth(count).text_content()[:15] == 'Высота потолков':
                                result[6] = (summary.nth(count).text_content()[15:-2])
                            else:
                                result[6] = random.choice(roof)

                            if result[5] == None:
                                if len(summary.nth(count).text_content()) > 13 and summary.nth(count).text_content()[:13] == 'Год постройки':
                                    result[5] = summary.nth(count).text_content()[13:]
                        try:
                            price = new_page.get_by_test_id('a10a3f92e9--input--qT5Pp').get_attribute('value', timeout=1000)
                            if price == '':
                                price = new_page.get_by_test_id('a10a3f92e9--input--YmTjn').first.get_attribute('value')
                        except PlaywrightTimeoutError:
                            price = new_page.get_by_test_id('a10a3f92e9--input--YmTjn').first.get_attribute('value')

                        price = price[:-6] + ',' + price[-6] + price[-5]
                        result[7] = price
                        print(result)
                        fill_line.writerow(result)
                        file.flush()

                    new_page.close()
                except PlaywrightTimeoutError:
                    pass

    context.close()
    context_map.close()


def main():
    with sync_playwright() as playwright:
        run_playwright(playwright)


if __name__ == '__main__':
    main()
