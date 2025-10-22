import asyncio
from pydoll.browser.chromium import Chrome
from pydoll.exceptions import ElementNotFound
from PIL import Image, ImageChops
import image_utils, nombres_utils
from google import genai
import imagehash
from flask import Flask, request, jsonify
from io import BytesIO
import base64
import logging
import os

GEMINI_MODEL=os.environ["MODEL"] 
API_KEY = os.environ["GEMINI_API"]

app = Flask(__name__)

app.logger.setLevel(logging.INFO)

async def adres_search(cc):
    async with Chrome() as browser:
        
        options = browser.options
        options.binary_location = '/usr/bin/google-chrome-stable'
        # https://peter.sh/experiments/chromium-command-line-switches/#disable-popup-blocking
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1024,1366')
        options.add_argument('--disable-dev-shm-usage') 
        #options.add_argument('--start-maximized')
        options.add_argument('--disable-popup-blocking')

        tab = await browser.start()
        await tab.enable_page_events()
        await tab.go_to('https://aplicaciones.adres.gov.co/bdua_internet/Pages/ConsultarAfiliadoWeb.aspx')
        await asyncio.sleep(5)

        
        search_box = await tab.find(tag_name="input", id='txtNumDoc')
        await search_box.type_text(cc)

        tries = 0
        while True:
            app.logger.info(cc+"-Try "+str(tries)+"/3")
            captcha_text = await captcha_solve(browser, tab)
            captcha_box = await tab.find(tag_name="input", id='Capcha_CaptchaTextBox')
            await captcha_box.type_text(captcha_text)

            consult_button = await tab.find(tag_name="input", id='btnConsultar')
            await consult_button.click()
            await asyncio.sleep(2)
            
            error_message = await tab.find(tag_name="span",id="Capcha_ctl00")
            is_visible = await error_message.is_visible()
            tries+=1

            if not is_visible:
                break
            if tries >= 3:
                await tab.close()
                await browser.stop()
                return "ERROR",cc,"Captcha no solucionado", None, None, None, None, None


        tab_respuesta = None
        tabs_opened = await browser.get_opened_tabs()
        for target in tabs_opened:
            current_url = await target.current_url
            if "RespuestaConsulta" in current_url:
                tab_respuesta = target

        
        if tab_respuesta is not None:
            current_url = await tab_respuesta.current_url
            app.logger.info(current_url)
            await tab_respuesta.bring_to_front()
            base64_screenshot = await tab_respuesta.take_screenshot(as_base64=True, beyond_viewport=True, quality=20)

            is_visible = False

            try:
                error_message = await tab_respuesta.find(tag_name="span",id="lblError")
                is_visible = await error_message.is_visible()
            except ElementNotFound:
                is_visible: False
            else:
                is_visible: True

            if is_visible:
                error_value = await error_message.text
                await tab_respuesta.close()
                await tab.close()
                await browser.stop()
                return "SUCCESS", cc, error_value, base64_screenshot, None, None, None, None
            else:
                estado_tag = await tab_respuesta.query('//*[@id="GridViewAfiliacion"]/tbody/tr[2]/td[1]')
                entidad_tag = await tab_respuesta.query('//*[@id="GridViewAfiliacion"]/tbody/tr[2]/td[2]')
                regimen_tag = await tab_respuesta.query('//*[@id="GridViewAfiliacion"]/tbody/tr[2]/td[3]')
                nombres_tag = await tab_respuesta.query('//*[@id="GridViewBasica"]/tbody/tr[4]/td[2]')
                apellidos_tag = await tab_respuesta.query('//*[@id="GridViewBasica"]/tbody/tr[5]/td[2]')

                estado  = await estado_tag.text
                entidad = await entidad_tag.text
                regimen = await regimen_tag.text
                nombres = await nombres_tag.text
                apellidos = await apellidos_tag.text

                await tab_respuesta.close()
                await tab.close()
                await browser.stop()
                nombre_completo = nombres +" "+ apellidos
                app.logger.info(nombre_completo)
                return "SUCCESS", cc, "", base64_screenshot, estado, entidad, regimen, nombres_utils.parsearNombre(nombre_completo)
        

        await asyncio.sleep(3)
        
        #https://pyimagesearch.com/2021/11/15/tesseract-page-segmentation-modes-psms-explained-how-to-improve-your-ocr-accuracy/
        
        #transformed = image_utils.algorithm1(captchaCrop)
        #captcha_text = pytesseract.image_to_string(transformed,
        #    config="--psm 13 -c tessedit_char_whitelist=0123456789")
        #cv2.imwrite("results/"+guid+"("+captcha_text.strip()+").png",cropped)
        #transformed.save("results/"+guid+"("+captcha_text.strip()+").png")
        #app.logger.info(captcha_text)
        
        #await tab.take_screenshot(path="fotito.png",beyond_viewport=True)
        #await asyncio.sleep(20)


async def captcha_solve(browser, tab):
    captcha = await tab.find(tag_name="img", id='Capcha_CaptchaImageUP')
    scr_image = captcha.get_attribute("src")
    scr_image= scr_image.replace("..","/bdua_internet")
    docs_tab = await browser.new_tab('https://aplicaciones.adres.gov.co'+scr_image)
    captcha_base64 = await docs_tab.take_screenshot(as_base64=True)
    await docs_tab.close()
    await asyncio.sleep(1)

    new_im = trim(Image.open(BytesIO(base64.b64decode(captcha_base64))))
    await asyncio.sleep(1)

    hash = imagehash.average_hash(new_im)
    #TODO: Add logic to validate if hash already exist to avoid call gemini
    hash_value = hash.__str__()
    new_im.save('results/'+hash_value+'.png')

    client = genai.Client(api_key=API_KEY)
    prompt = "Please analyze this CAPTCHA image. The image only contains numbers/digits with " \
    "some noise/distortion. Return only the CAPTCHA numbers without any additional text or explanation. The CAPTCHA always contains 5 digits"

    contents = [
        new_im,       # The image data
        prompt     # The text prompt
    ]

    response = client.models.generate_content(
        model=GEMINI_MODEL, 
        contents=contents
    )
    code="00000"
    if response.text==None:
        code = "00000" 
    else:
        code= response.text
    new_im.save('results/'+hash_value+'('+code+').png')

    # 6. Print the response
    app.logger.info("--- Gemini Analysis --->"+code)
    return response.text
    

def trim(im):
    bg = Image.new(im.mode, im.size, im.getpixel((0,0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    #Bounding box given as a 4-tuple defining the left, upper, right, and lower pixel coordinates.
    #If the image is completely empty, this method returns None.
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)

@app.route('/login', methods=['GET'])
def login():
    document_to_search = request.args.get('document', '')
    status, document, message, imagebase64, estado, entidad, regimen, nombres =  asyncio.run(adres_search(document_to_search))
    my_dict = {
        "status": status,
        "document": document,
        "message": message,
        "imageBase64": imagebase64,
        "estado": estado,
        "entidad": entidad,
        "regimen": regimen
    }
    if (nombres != None):
        my_dict["pnombre"]= nombres["pnombre"] if "pnombre" in nombres else ""
        my_dict["snombre"]=nombres["snombre"] if "snombre" in nombres else ""
        my_dict["papellido"]=nombres["papellido"] if "papellido" in nombres else ""
        my_dict["sapellido"]=nombres["sapellido"] if "sapellido" in nombres else ""

    if status=="SUCCESS":
        return jsonify(my_dict), 200
    else:
        return jsonify(my_dict), 500

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=19999)