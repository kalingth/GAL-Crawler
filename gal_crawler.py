from requests import get, post
from urllib3 import disable_warnings, exceptions
from sys import argv
from xlsxwriter import Workbook

class get_swab_result:
    """
    A class to manipulate the GAL(Gerenciador de Ambiente Laboratorial).

    This class will generate a report with the data of persons who tested with SWAB into Sistema Único de Saúde do Rio de Janeiro:

    ...
    Attributes
    ----------
    __header_paciente : dict
        An internal attribute that represents the header of the query used to get sick's personal data.
    __header_result : dict
        An internal attribute that represents the header of the query used to get the SARS-COV-2 diagnosis.
    __results : list
        An internal list that contains the collected data from GAL.
    __ids : tuple
        An internal tuple that contains a list of ids to run that crawler.
    
    Methods
    -------
    login() -> bool
        That method will retrieve the PHPSESSID Cookie using the user/password auth set by the user. That Cookie is very important to use that application.
    list_generate(init: str, end: str, unidade: str = None) -> bool
        That method will, obligatory, receive an initial date and a final date and, optionally, a health unit. Will make a request and generate a list of ids based on the response to that request.
    result() -> tuple
        A method that return a tuple that contains the return obteined with run method.
    __get_results__(id: str) -> tuple
        An internal method that receives an id and returns a list of collected data from GAL.
    clear() -> None
        A method used to clear the following attributes: __ids and __results.
    run() -> bool
        That method initialize the crawler and feed __get_results__ with id. Returns True if run all data with success or False if an issue occurs.
    save_output(name: str) -> None
        That method save collected data from the crawler into an excel file.
    load_ids() -> tuple
        That method will return a tuple generated from a file that contains a list of ids separated with a break line.
    """
    
    __header_paciente: dict = {
        "Accept-Language": "pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://gal.riodejaneiro.sus.gov.br/bmh/consulta-paciente-laboratorio/",
        "X-Requested-With": "XMLHttpRequest", "Connection": "keep-alive", "Pragma": "no-cache",
        "Cache-Control": "no-cache"}
    __header_result: dict = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3", "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive", "Referer": "https://gal.riodejaneiro.sus.gov.br/bmh/consulta-paciente-laboratorio/",
        "Upgrade-Insecure-Requests": "1"}
    __result: list = []
    __ids: tuple = ()


    class LoginException(SystemError: object):
        pass


    def __init__(self: object, login: str, password: str, load: bool = False,
                    init_date: str = None, end_date: str = None, unidade: str = None) -> object:
        """
        Constructs all the necessary attributes for the crawler object.

        Parameters
        ----------
            login: str
                User account for GAL.
            password: str
                User password for GAL.
            load: bool, optional
                That variable needs to set as True if you want to load a file that contains a list of ids or if you want to set the id list using the constructor.
            init_date: str, optional
                That variable is required if the load is set as False, otherwise will return an error message. The input format expected is "dd/mm/YYYY". That variable represents the beginning of the range of dates.
            end_date: str, optional
                That variable is required if the load is set as False, otherwise will return an error message. The input format expected is "dd/mm/YYYY". That variable represents the ending of the range of dates.
            unidade: str, optional
                That variable will be used to filter the id list by health unit which collected the RT-PCR exam.
        """
        disable_warnings(exceptions.InsecureRequestWarning)
        
        self.user = login
        self.passwd = password
        
        checker = self.login()

        if not checker:
            raise self.LoginException("Invalid login parameters!")
        
        if load:
            self.__ids = self.load_ids()

        elif init_date and end_date:
            self.list_generate(init_date, end_date, unidade)

        else:
            raise ValueError(
                "If you don't wish to load ids from a file or set it, please set an initial date and an end date.")


    def login(self: object) -> bool:
        """
        That method will receive the PHPSESSID cookie from the server using a pre-setted user account and password.
        """
        main_header: dict = {
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': '*/*'}
        
        get_login = f"https://gal.riodejaneiro.sus.gov.br/login/laboratorio/?login={self.user}&senha={self.passwd}&laboratorio=5670268&modulo=BMH&_dc=1620160954425"
        req_login = get(get_login, verify=False, headers=main_header)
        if req_login.json()["success"]:
            cookies = req_login.headers['Set-Cookie']
            self.__header_result['Cookie'] = self.__header_paciente['Cookie'] = cookies.split(';')[0]
            return True
        return False


    @property
    def result(self: object) -> tuple:
        """
        That property will return the internal attribute __result(get method).
        """
        return tuple(self.__result)


    def list_generate(self: object, init: str, end: str, unidade: str = None) -> bool:
        """
        That function will search into GAL to generate a list of ids that satisfy the following query:
            - The RT-PCR should be collected in the range created by init(initial date) and end(final date);
            - The RT-PCR should be collected into an informed unit(unidade). But that parameter is doesn't require.;
        
        Parameters
        ----------
            init: str
                That variable represents the initial date. Expect the following format: dd/mm/yyyy
            end: str
                That variable represents the final date. Expect the following format: dd/mm/yyyy
            unidade: str, optional
                That variable may contain the health unit which collected the RT-PCR.
        """
        # Setting the headers to send the request.
        post_header = {"Referer": "https://gal.riodejaneiro.sus.gov.br/bmh/consulta-exame-laboratorio/",
                       "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                       "Accept-Language": "pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3",
                       "Origin": "https://gal.riodejaneiro.sus.gov.br",
                       "Cookie": self.__header_paciente['Cookie'],
                       "Accept-Encoding": "gzip, deflate, br",
                       "Host": "gal.riodejaneiro.sus.gov.br",
                       "X-Requested-With": "XMLHttpRequest",
                       "Cache-Control": "no-cache",
                       "Connection": "keep-alive",
                       "Pragma": "no-cache",
                       "Accept": "*/*"}

        # Preparing the body of post request.
        body = f"method=post&start=0&exame=&status=&cancelado=true&dtInicio=%22{'-'.join(init.split('/')[::-1])}T00%3A00%3A00%22&dtFim=%22{'-'.join(end.split('/')[::-1])}T00%3A00%3A00%22"
        req_filter = f"&filter%5B0%5D%5Bfield%5D=unidade&filter%5B0%5D%5Bdata%5D%5Btype%5D=string&filter%5B0%5D%5Bdata%5D%5Bvalue%5D={unidade.replace(' ', '%20')}"
        body += req_filter if unidade else ''

        # Making the request
        url = "https://gal.riodejaneiro.sus.gov.br/bmh/consulta-exame-laboratorio/lista/"
        response = post(url, data=body, headers=post_header, verify=False).json()
        if 'message' in response.keys():
            if response['message'] == "O usuário não está autenticado ou a sessão expirou":
                message = "The informed Cookie is not a valid Cookie. Please, open your GAL account and get your \
                           PHPSESSID Cookie before continue."
                print(f"\n{'-'*len(message)}\n{message}\n{'-'*len(message)}")
                self.__ids = ()
                return False

        # Saving the returned data from GAL.
        self.__ids = tuple(str(i['requisicao']) for i in response['dados'] if i["status"] == "Resultado Liberado")
        message = f"| {len(self.__ids)} ids have been found between {init} and {end} for the unit {unidade.title() if unidade else 'Geral'} |"
        print(f"\n{'-' * len(message)}\n{message}\n{'-' * len(message)}\n")
        return True


    def __get_results__(self: object, req_id: str) -> tuple:
        """
        That internal method will send two requests to GAL and will 
        
        Parameters
        ----------
            req_id: str
                A string that contains the exam id into GAL.
        """
        url_paciente = f"https://gal.riodejaneiro.sus.gov.br/bmh/consulta-paciente-laboratorio/carregar/?requisicao={req_id}"
        url_result = f'https://gal.riodejaneiro.sus.gov.br/bmh/consulta-paciente-laboratorio/imprimir-resultado/?requisicoes=["{req_id}"]'
        paciente = get(url_paciente, headers=self.__header_paciente, verify=False).json()
        result = get(url_result, headers=self.__header_result, verify=False).text
        result = "Detectável" if result.count("<u>Detectável:</u>") else "Não Detectável" if result.count(
            "<u>Não Detectável:</u>") else "Inconclusivo"

        return_data = (paciente['requisicao']['dataSolicitacao'],
                       paciente['requisicao']['paciente']['nome'],
                       paciente['requisicao']['paciente']['cns'],
                       paciente['requisicao']['paciente']['cpf'],
                       paciente['requisicao']['paciente']['dataNascimento'],
                       paciente['requisicao']['paciente']['idadeComp'],
                       paciente['requisicao']['paciente']['sexo'],
                       str(paciente['requisicao']['paciente']['logradouro']) + ' ' + str(
                           paciente['requisicao']['paciente']['numeroLogradouro']),
                       paciente['requisicao']['paciente']['bairro'],
                       paciente['requisicao']['paciente']['cep'],
                       result)
        return return_data


    def clear(self: object) -> None:
        """
        That method will delete the data stored into internal attributes.
        """
        self.__result = []
        self.__ids = ()


    def run(self: object, root: object = None, tkresponse: object = None) -> bool:
        """
        That class will initialize the crawler and will feed the internal method __get_results__ which will return received data from GAL.
        """
        self.root = root
        try:
            print("\nPlease, wait while the crawler's running...")
            for i in range(len(self.__ids)):
                if tkresponse:
                    tkresponse['text'] = f"Coletando dados do paciente {i+1} de {len(self.__ids)}"
                self.root.update() if self.root else None
                req_id = self.__ids[i]
                self.__result.append(self.__get_results__(req_id))
        except KeyboardInterrupt:
            print("The crawler has been stopped by the user.\n")
            return False
        except:
            return False
        self.__result.sort(key=lambda x: x[0].split('/')[::-1])
        return True


    def save_output(self: object, name: str) -> None:
        """
        That method will receive a name and will save in an Excel file with that name which contains the received data from GAL.
        
        Parameters
        ----------
            name: str
                The name of the output file.
        """
        output = [['Data Coleta', 'Nome do Paciente', 'CNS', 'CPF', 'Nascimento', 'Idade', 'Sexo', 'Endereço', 'Bairro',
                   'CEP', 'Resultado']]
        output.extend(self.__result)
        name = name if '.xlsx' in name else f'{name}.xlsx'
        with Workbook(name) as workbook:
            worksheet = workbook.add_worksheet("GAL Report")

            for row_num, data in enumerate(output):
                worksheet.write_row(row_num, 0, data)


    def load_ids(self: object) -> None:
        """
        That method will get input files from users and will read a list of ids from that file.
        """
        idIn = input("Enter with the name of the archive that contains a list of ids separated with break line: ")
        with open(idIn) as file:
            data = filter(bool, file.read().split('\n'))
        return tuple(data)



def askyesornot(message):
    """
    An auxiliary function to ask anything and await for y(yes) or n(no).
    """
    response = None
    while not response:
        response = input(f"{message} (y/n)").lower()
        response = None if response not in ('y', 'n') else response
        if response == 'y':
            return True
        elif response == 'n':
            return False


if __name__ == "__main__":
    if len(argv) >= 3:
        parameters = {"login":argv[1],
                      "password":argv[2],
                      "init_date": argv[3],
                      "end_date": argv[4],
                      "unidade": " ".join(argv[5:])}
    else:
        parameters = {"login": input("Please, insert your user account:"),
                      "password": input("Please, insert your password account:"),
                      "init_date": input("Please, set the initial date(use this format: dd/mm/yyyy):"),
                      "end_date": input("Please, set the final date(use this format: dd/mm/yyyy):"),
                      "unidade": input("If you want, set a health unit that collects the RT-PCR to filter the search:")}

    crawler = get_swab_result(**parameters)
    if crawler.run():
        print("Success!! The spider caught all data! :)\n")
        if askyesornot("You want to save data?"):
            crawler.save_output(input("Choose a name for your output:"))
    else:
        print("Fail!! The spider has been killed! :(\n\n")
