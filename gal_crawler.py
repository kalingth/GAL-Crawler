from requests import get
from urllib3 import disable_warnings, exceptions

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
    result() -> tuple
        A method that return a tuple that contains the return obteined with run method.
    __get_results__(id: str) -> tuple
        An internal method that receives an id and returns a list of collected data from GAL.
    clear() -> None
        A method used to clear the following attributes: __ids and __results.
    run() -> bool
        That method initialize the crawler and feed __get_results__ with id. Returns True if run all data with success or False if an issue occurs.
    save_output(name: str) -> None
        That method save collected data from the crawler into a csv file.
    load_ids() -> tuple
        That method will return a tuple generated from a file that contains a list of ids separated with a break line.
    load_cookie() -> str
        That method will get the PHPSESSID cookie with the user.
    """
    __header_paciente: dict =  {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0","Accept": "*/*","Accept-Language":"pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3","Referer": "https://gal.riodejaneiro.sus.gov.br/bmh/consulta-paciente-laboratorio/","X-Requested-With": "XMLHttpRequest","Connection": "keep-alive","Pragma": "no-cache","Cache-Control": "no-cache"}
    __header_result: dict = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8","Accept-Language": "pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3","Accept-Encoding": "gzip, deflate, br","Connection": "keep-alive","Referer": "https://gal.riodejaneiro.sus.gov.br/bmh/consulta-paciente-laboratorio/","Upgrade-Insecure-Requests": "1"}
    __result: list = []
    __ids: tuple = ()


    def __init__(self: object, ids: tuple = None, PHPSESSID: str = None) -> object:
        """
        Constructs all the necessary attributes for the person object.

        Parameters
        ----------
            ids: tuple, optional
                A tuple that contains a list of ips, but isn't required.
            PHPSESSID: str, optional
                A string that contains a session cookie from GAL.
        """
        self.__header_result['Cookie'] = self.__header_paciente['Cookie'] = f"PHPSESSID={PHPSESSID}" if PHPSESSID else self.load_cookie()
        self.__ids = ids if ids else self.load_ids()
        disable_warnings(exceptions.InsecureRequestWarning)

    @property
    def result(self: object) -> tuple:
        """
        That property will return the internal attribute __result(get method).
        """
        return tuple(self.__result)


    def __get_results__(self: object, id: str) -> tuple:
        """
        That internal method will send two requests to GAL and will 
        
        Parameters
        ----------
            id: str
                A string that contains the exam id into GAL.
        """
        url_paciente = f"https://gal.riodejaneiro.sus.gov.br/bmh/consulta-paciente-laboratorio/carregar/?requisicao={id}"
        url_result = f'https://gal.riodejaneiro.sus.gov.br/bmh/consulta-paciente-laboratorio/imprimir-resultado/?requisicoes=["{id}"]'
        paciente = get(url_paciente, headers=self.__header_paciente, verify=False).json()
        result = get(url_result, headers=self.__header_result, verify=False).text
        result = "Detectável" if result.count("<u>Detectável:</u>") else "Não Detectável" if result.count("<u>Não Detectável:</u>") else "Inconclusivo"
        return_data =  (paciente['requisicao']['dataSolicitacao'],
                        paciente['requisicao']['paciente']['nome'],
                        paciente['requisicao']['paciente']['cns'],
                        paciente['requisicao']['paciente']['cpf'],
                        paciente['requisicao']['paciente']['dataNascimento'],
                        paciente['requisicao']['paciente']['idadeComp'],
                        paciente['requisicao']['paciente']['sexo'],
                        str(paciente['requisicao']['paciente']['logradouro']) + ' ' + str(paciente['requisicao']['paciente']['numeroLogradouro']),
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


    def run(self: object) -> bool:
        """
        That class will initialize the crawler and will feed the internal method __get_results__ which will return received data from GAL.
        """
        try:
            print("\nPlease, wait while the crawler's running...")
            for i in range(len(self.__ids)):
                id = self.__ids[i]
                self.__result.append(self.__get_results__(id))
        except:
            return False
        self.__result.sort(key=lambda x: x[0].split('/')[::-1])
        return True


    def save_output(self: object, name: str) -> None:
        """
        That method will receive a name and will save a .csv file with that name which contains the received data from GAL.
        
        Parameters
        ----------
            name: str
                The name of the output file.
        """
        output = [['Data Coleta', 'Nome do Paciente','CNS','CPF','Nascimento','Idade','Sexo','Endereço','Bairro','CEP','Resultado']]
        output.extend(self.__result)
        with open(f'{name}.csv', 'w') as file:
            file.write("\n".join(';'.join(map(lambda x: str(x) if x else '',line)) for line in output))


    def load_ids(self: object) -> None:
        """
        That method will get input files from users and will read a list of ids from that file.
        """
        idIn = input("Enter with the name of the archive that contains a list of ids separated with break line: ")
        with open(idIn) as file:
            data = filter(bool, file.read().split('\n'))
        return tuple(data)


    def load_cookie(self: object) -> None:
        """
        That method will receive the PHPSESSID cookie from the user and will return it.
        """
        PHPSESSID = input("Now, enter with the cookie(PHPSESSID) of your session on GAL(Gerenciador de Ambiente Laboratorial): ")
        return f"PHPSESSID={PHPSESSID}"


if __name__ == "__main__":
    crawler = get_swab_result()
    if crawler.run():
        print("Success!! The spider caught all data! :)\n")
        save = None
        while save == None:
            check = input("You want to save data? (y/n) ")
            if check == 'y':
                name = input("Choose a name for your output: ")
                crawler.save_output(name)
                break
            elif check == 'n':
                break
    else:
        print("Fail!! The spider has been killed! :(\n\n")
