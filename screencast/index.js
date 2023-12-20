import puppeteer from "puppeteer"

const sleep = async time => await new Promise(resolve => setTimeout(resolve, time))

const type = async text => {
    await page.keyboard.type(text, { delay: 25 })
    await sleep(250)
    await page.keyboard.press("Enter")
}

const waitForMessage = async text => {
    await page.waitForFunction(text => {
        const messages = document.querySelectorAll(".text-content.clearfix.with-meta")
        const lastMessage = messages[messages.length - 1]
        return lastMessage.textContent.includes(text)
    }, {}, text)
}

const scroll = async (deltaY, times) => {
    await page.mouse.move(900, 300)
    for (let i = 0; i < times; i++) {
        await page.mouse.wheel({ deltaY })
        await sleep(10)
    }
}

const browser = await puppeteer.launch({ headless: false, args: ["--start-fullscreen"] })
const page = await browser.newPage()

await page.setViewport({ width: 1000, height: 500 })
await page.goto("https://web.telegram.org/a/")

const area = await page.waitForSelector("#MiddleColumn", { timeout: 0 })
const start = await page.waitForSelector(".Button.tiny.primary.fluid.has-ripple", { timeout: 0 })
await sleep(2000)

const box = await area.boundingBox()
box.x += 1
box.width -= 1

const rec = await page.screencast({ crop: box, path: "screencast.webm" })

await sleep(1000)
await start.click()

const input = await page.waitForSelector("#editable-message-text")
await input.click()

await sleep(2000)
await type("Привет! Мне бы хотелось съездить в Лондон.")
await waitForMessage("Сейчас ваш запрос выглядит так")

await sleep(2000)
await type("У меня там будет важная встреча вечером 31 декабря.")
await waitForMessage("Сейчас ваш запрос выглядит так")

await sleep(2000)
await type("Сам я из Екб, а вернуться планирую где-то 8 числа.")
await waitForMessage("Вот, что мне удалось найти")

await sleep(2000)
await scroll(-10, 90)
await sleep(500)
await scroll(20, 50)

await sleep(500)
await type("Вот это я понимаю! Реально крутой бот.")

await sleep(350)
await rec.stop()
await browser.close()
