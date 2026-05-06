import customtkinter as ctk

app = ctk.CTk()
app.geometry("400x200")

entry = ctk.CTkEntry(app, justify="right", font=("Cairo", 20), width=300)
entry.pack(pady=50)

app.mainloop()
