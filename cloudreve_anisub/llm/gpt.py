# TODO
class GPTChatCompletion:
    def __init__(self, model_name="gpt2-medium"):
        self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        self.model = GPT2LMHeadModel.from_pretrained(model_name)
        self.model.eval()
        self.model.to("cuda")

    def generate(self, text):
        input_ids = self.tokenizer.encode(text, return_tensors="pt").to("cuda")
        output = self.model.generate(input_ids, max_length=100, num_return_sequences=1)
        return self.tokenizer.decode(output[0], skip_special_tokens=True)