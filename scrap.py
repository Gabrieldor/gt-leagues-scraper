from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import datetime
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import ElementClickInterceptedException
import gspread
from google.oauth2.service_account import Credentials


def get_date():
    last_date = wait.until(EC.visibility_of_element_located((By.XPATH, "//h6[@class='MuiTypography-root MuiTypography-h6']")))
    last_date = last_date.text.split(":")[1][1:]
    s_last_date = last_date.split(" ")
    last_date = datetime.datetime(int(s_last_date[2]),
                              int(datetime.datetime.strptime(s_last_date[1], "%b").month),
                              int(s_last_date[0]))
    return last_date

def get_data(driver):

    h3_s = wait.until(EC.visibility_of_element_located((By.XPATH, "//div[@class='my-2']/h3"))).text.split('/')
    tour_date = h3_s[2].split('(')

    date = tour_date[1][:-1]
    time = driver.find_element(By.XPATH, "//div[@class='m-4 date-time-wrapper']/p[2]").text

    
    group = h3_s[1][1:-1]
    tournament = tour_date[0][1:-1]

    p1 = driver.find_element(By.XPATH, "//div[@class='z-10 flex items-center justify-center flex-1 py-4 text-center']/div[2]//h4").text
    t1 = driver.find_element(By.XPATH, "//div[@class='z-10 flex items-center justify-center flex-1 py-4 text-center']/div[2]//h6").text
    try:
        s1 = int(driver.find_element(By.XPATH, "//div[@class='z-10 flex items-center justify-center flex-1 py-4 text-center']/div[2]//span[@class='score px-4 ended']").text)
    except:
        s1 = "PARTIDA DESISTIDA"

    p2 = driver.find_element(By.XPATH, "//div[@class='z-10 flex items-center justify-center flex-1 py-4 text-center']/div[4]//h4").text
    t2 = driver.find_element(By.XPATH, "//div[@class='z-10 flex items-center justify-center flex-1 py-4 text-center']/div[4]//h6").text
    try:
        s2 = int(driver.find_element(By.XPATH, "//div[@class='z-10 flex items-center justify-center flex-1 py-4 text-center']/div[4]//span[@class='score px-4 ended']").text)
    except:
        s2 = "PARTIDA DESISTIDA"

    result = [date,time,group,tournament,p1,t1,s1,p2,t2,s2]
    print (result)

    return result

def connect_spreadsheet():
    scopes = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    json_file = "cred.json"
    credentials = Credentials.from_service_account_file(json_file,scopes=scopes)
    gc = gspread.authorize(credentials)
    return gc

def restart_browser():
    global driver

    driver.close()
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'})
    wait = WebDriverWait(driver, 10)
    actions = ActionChains(driver)
    time.sleep(5)
    driver.get("https://www.gtleagues.com/past-results")

    return driver, wait, actions

def move_to_date(prev):
    global max
    global max_table
    global max_footer

    i = 4
    date = get_date()
    while date > target_date:
        wait.until(EC.visibility_of_element_located((By.XPATH, "//td[@class='MuiTableCell-root MuiTableCell-body MuiTableCell-alignLeft']")))
        if i > 0:
            actions.move_to_element(driver.find_element(By.XPATH, f"//div[@class='flex justify-center p-4 my-4 bg-white']/div[{i}]")).perform()
            driver.find_element(By.XPATH, f"//div[@class='flex justify-center p-4 my-4 bg-white']/div[{i}]").click()
        else:
            actions.move_to_element(driver.find_element(By.XPATH, "//div[@class='flex justify-center p-4 my-4 bg-white']/button")).perform()
            driver.find_element(By.XPATH, "//div[@class='flex justify-center p-4 my-4 bg-white']/button").click()
        
        date = get_date()
        i -= 1
    wait.until(EC.visibility_of_element_located((By.XPATH, "//div[@class='MuiInputBase-root MuiTablePagination-input MuiTablePagination-selectRoot jss4']")))
    actions.move_to_element(driver.find_element(By.XPATH, "//div[@class='MuiInputBase-root MuiTablePagination-input MuiTablePagination-selectRoot jss4']")).perform()

    wait.until(EC.visibility_of_element_located((By.XPATH, "//td[@class='MuiTableCell-root MuiTableCell-body MuiTableCell-alignLeft']")))
    wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@class='MuiInputBase-root MuiTablePagination-input MuiTablePagination-selectRoot jss4']"))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@class='MuiPaper-root MuiMenu-paper MuiPopover-paper MuiPaper-elevation1 MuiPaper-rounded']//li[4]"))).click()
    if prev == False:
        time.sleep(5)
        try:
            wait.until(EC.visibility_of_element_located((By.XPATH, "//div[@class='jss14']/span[5]/button"))).click()
        except ElementClickInterceptedException:
            time.sleep(5)
            try:
                wait.until(EC.visibility_of_element_located((By.XPATH, "//div[@class='jss14']/span[5]/button"))).click()
            except:
                pass
        except:
            pass
        time.sleep(5)

    s_footer = driver.find_element(By.XPATH, "//span[@class='MuiTypography-root MuiTypography-caption']").text.split(' ')
    max = int(s_footer[2])

    ss_footer = s_footer[0].split("-")
    max_table = int(ss_footer[1]) - int(ss_footer[0]) + 1
        
def get_info(gc):
    spreadsheet = gc.open("Resultados")
    sheet = spreadsheet.worksheet("Folha1")
    dados = sheet.get_all_records()
    res = []
    for d in dados:
        res.append(list(d.values()))
    return res

def scrap():
    global z
    global y
    global wait
    global driver
    global prev
    global actions
    global dup
    global target_date
    global choice
    global supress
    
    r = False
    wait.until(EC.visibility_of_element_located((By.XPATH, "//td[@class='MuiTableCell-root MuiTableCell-body MuiTableCell-alignLeft']")))
    time.sleep(10)
    actions.move_to_element(driver.find_element(By.XPATH, f"//tbody[@class='MuiTableBody-root']/tr[{z}]")).perform()
    driver.find_element(By.XPATH, f"//tbody[@class='MuiTableBody-root']/tr[{z}]").click()
    info = get_data(driver)
    if info not in dados:
        print("Saving data in the spreadsheet")
        ss.insert_row(info, index=2)
        dup = 0
    elif info == dados[1]:
        print("Duplicate data detected, data not saved. Scraping next data")
        dup += 1
    else: print("Duplicate data detected, data not saved. Scraping next data")

    z-=1
    y+=1

    if y == 10:
        driver, wait, actions = restart_browser()
        move_to_date(prev)
        y = 0
        r = True
    if z <= 0 and choice != 2:
        if prev == True:
            if target_date.date() != datetime.datetime.today().date(): 
                prev = False
                target_date = target_date + datetime.timedelta(days=1)
                driver, wait, actions = restart_browser()
            else:
                supress = True
                print("Acabaram os jogos, aguardando 15 minutos")
                time.sleep(900)
                driver, wait, actions = restart_browser()
                get_last()
            
        else:
            prev = True
            driver, wait, actions = restart_browser()

        move_to_date(prev)
        time.sleep(5)
       

        s_footer = driver.find_element(By.XPATH, "//span[@class='MuiTypography-root MuiTypography-caption']").text.split(' ')
        ss_footer = s_footer[0].split("-")
        max_table = int(ss_footer[1]) - int(ss_footer[0]) + 1

        z=max_table

        
        r = True

        
    if r == False:
        driver.get("https://www.gtleagues.com/past-results")
        move_to_date(prev)
    else:
        r = False
    
def get_last():
    global hora
    global player
    global dados
    global z
    global wait
    global driver
    global prev
    global target_date

    dados = get_info(gc)
    for dado in dados:
        if "-" in dado[0]:
            dsplit = dado[0].split('-')
            dd = dsplit[0]
            dm = dsplit[1]
            da = dsplit[2]
            target_date = datetime.datetime(int(da),int(dm),int(dd))
            hora = dado[1]
            player = dado[4]
            break
    
    found = False
    move_to_date(prev)
    wait.until(EC.visibility_of_element_located((By.XPATH, "//td[@class='MuiTableCell-root MuiTableCell-body MuiTableCell-alignLeft']")))
    rows = driver.find_elements(By.XPATH, "//tr[@class='MuiTableRow-root MuiTableRow-hover']")
    for row in rows:
        ldata = str(target_date).split(' ')[0].split('-')
        ndata = f'{ldata[2]}/{ldata[1]}/{ldata[0]}'
        texto = row.text
        if ndata in texto and hora in texto and player in texto:
            z = int(row.get_attribute("index")) + 1
            found = True
            break
    if found == False:
        time.sleep(5)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@class='jss14']/span[2]"))).click()
        time.sleep(10)
        wait.until(EC.visibility_of_element_located((By.XPATH, "//td[@class='MuiTableCell-root MuiTableCell-body MuiTableCell-alignLeft']")))
        rows = driver.find_elements(By.XPATH, "//tr[@class='MuiTableRow-root MuiTableRow-hover']")
        for row in rows:
            ldata = str(target_date).split(' ')[0].split('-')
            ndata = f'{ldata[2]}/{ldata[1]}/{ldata[0]}'
            texto = row.text
            if ndata in texto and hora in texto and player in texto:
                z = int(row.get_attribute("index")) + 1
                
                prev = True
                break

def work():
    global choice
    global target_date
    global actions
    global driver
    global y
    global dup
    global prev
    global z
    global results
    global wait
    global dados
    global player
    global hora
    global supress
    
    try:
        wait = WebDriverWait(driver, 30)
        actions = ActionChains(driver)
        results = []
        prev = False
        supress = False

        if choice == 1:
            data_escolhida = input("Insira a data desejada (formato dd-m-aaaa, exemplo: 25-8-2022): ")
            dsplit = data_escolhida.split('-')
            dd = dsplit[0]
            dm = dsplit[1]
            da = dsplit[2]
            target_date = datetime.datetime(int(da),int(dm),int(dd))
            dados = get_info(gc)

        if choice == 3:
            get_last()
             
        print("Scraping desired info:")

        if choice != 3:
            move_to_date(prev)

            z=max_table

        y=0
        dup=0

        if choice != 2:
            while dup < 3:
                scrap()
                if choice == 2: break
                
        driver, wait, actions = restart_browser()

    except Exception as e:
        if supress == False:
            print(e)
            print("Ocorreu um erro, recomeçando a partir da ultima informação coletada")
        choice = 3
        driver, wait, actions = restart_browser()
        work()   

gc = connect_spreadsheet()
ss = gc.open("Resultados").sheet1
chrome_options = Options()
chrome_options.headless = True
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'})
driver.get("https://www.gtleagues.com/past-results")
choice = 4

print("Starting program\n")

while choice != 1 and choice != 2 and choice != 3:
    print("Escolha o que vc deseja realizar")
    print("1 - Coletar partidas a partir de uma data especifica")
    print("2 - Coletar partidas novas a partir de agora")
    print("3 - Continuar a coleta anterior")
    try:
        choice = int(input())
    except:
        choice = 712
    if choice != 1 and choice != 2 and choice != 3:
        print("Opção invalida, favor escolher apenas uma das opções apresentadas\n")

work()
    

    
            

   

    
    

