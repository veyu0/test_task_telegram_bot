from create_bot import dp
from aiogram.utils import executor
from handlers import main_handlers


# запуск бота
async def on_startup(_):
    print('Бот запущен')


main_handlers.register_handlers_main(dp)

executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
