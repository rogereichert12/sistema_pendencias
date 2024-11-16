from faker import Faker

# Configurar Faker para saída compatível com UTF-8
fake = Faker('pt_BR', use_weighting=True)

num_registros = 100
sql_commands = []

for _ in range(num_registros):
    aluno = fake.name()
    responsavel = fake.name()
    cpf = fake.unique.random_number(digits=11, fix_len=True)
    telefone = fake.unique.random_number(digits=11, fix_len=True)
    
    # Formata o comando SQL
    sql = f"INSERT INTO `controle_financeiro`.`clientes` (`aluno`, `responsavel`, `cpf`, `telefone`) VALUES ('{aluno}', '{responsavel}', '{cpf}', '{telefone}');"
    sql_commands.append(sql)

# Salva os comandos SQL em um arquivo .sql usando UTF-8
with open("inserts_clientes.sql", "w", encoding="utf-8") as file:
    for command in sql_commands:
        file.write(command + "\n")

print("Arquivo 'inserts_clientes.sql' gerado com sucesso!")
