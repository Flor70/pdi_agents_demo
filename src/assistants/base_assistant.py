from openai import OpenAI
from pathlib import Path
import asyncio


class BaseAssistant:
    """Classe base para todos os assistentes do sistema."""

    def __init__(self, openai_api_key, model="gpt-4o"):
        """Inicializa o assistente com a chave da API OpenAI e configurações padrão.

        Args:
            openai_api_key (str): Chave da API OpenAI
            model (str, optional): Modelo a ser usado. Padrão é "gpt-4o".
        """
        self.client = OpenAI(api_key=openai_api_key)
        self.assistant = None
        self.thread = None
        self.model = model

    def initialize_assistant(self, name, instructions):
        """Inicializa o assistente com instruções específicas.

        Args:
            name (str): Nome do assistente
            instructions (str): Instruções detalhadas para o assistente
        """
        self.assistant = self.client.beta.assistants.create(
            name=name,
            instructions=instructions,
            model=self.model
        )
        return self.assistant

    def create_thread(self):
        """Cria um novo thread se ainda não existir"""
        if self.thread is None:
            self.thread = self.client.beta.threads.create()
        return self.thread

    def upload_documents(self, files_to_read, output_dir, additional_prompt=""):
        """Lê o conteúdo dos documentos e cria uma mensagem com o contexto.

        Args:
            files_to_read (list): Lista de arquivos a serem lidos
            output_dir (str): Diretório onde os arquivos estão localizados
            additional_prompt (str, optional): Texto adicional a ser incluído após o contexto

        Returns:
            str: Uma string de contexto com o conteúdo de todos os arquivos
        """
        output_path = Path(output_dir)
        context = []

        # Tenta ler os arquivos do diretório especificado
        for filename in files_to_read:
            file_path = output_path / filename
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    context.append(f"Conteúdo de {filename}:\n\n{content}\n\n")

        # Se não encontrou arquivos, busca em um diretório alternativo
        if not context:
            alt_path = Path(output_dir).parent.parent / "output"
            for filename in files_to_read:
                file_path = alt_path / filename
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        context.append(
                            f"Conteúdo de {filename}:\n\n{content}\n\n")

        if not context:
            raise ValueError(
                f"Nenhum documento encontrado no diretório especificado: {output_dir}")

        context_string = "Aqui está o contexto dos documentos:\n\n" + \
            "\n".join(context)
        if additional_prompt:
            context_string += f"\n\n{additional_prompt}"

        # Criar thread com o contexto
        self.thread = self.client.beta.threads.create(
            messages=[{
                "role": "user",
                "content": context_string
            }]
        )

        return context_string

    async def get_response(self, user_message):
        """Obtém resposta do assistente para a mensagem do usuário.

        Args:
            user_message (str): Mensagem do usuário

        Returns:
            str: Resposta do assistente
        """
        if not self.thread:
            self.create_thread()

        # Adiciona a mensagem do usuário ao thread
        self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=user_message
        )

        # Cria um run
        run = self.client.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id=self.assistant.id
        )

        # Aguarda a conclusão do run
        while True:
            run = self.client.beta.threads.runs.retrieve(
                thread_id=self.thread.id,
                run_id=run.id
            )
            if run.status == 'completed':
                break
            elif run.status == 'failed':
                return "Ocorreu um erro ao processar sua solicitação."
            await asyncio.sleep(0.5)

        # Obtém a resposta do assistente
        messages = self.client.beta.threads.messages.list(
            thread_id=self.thread.id
        )

        # Retorna a última mensagem do assistente
        for msg in messages.data:
            if msg.role == "assistant":
                return msg.content[0].text.value

        return "Não foi possível gerar uma resposta."
