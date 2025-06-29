import os
from dotenv import load_dotenv

load_dotenv()
mode = os.environ.get("MODE", "api")
port = int(os.environ.get("PORT", 5000))

if mode == "record":
    from record import main
    main()
else:
    from api import app
    app.run(host="0.0.0.0", port=port)