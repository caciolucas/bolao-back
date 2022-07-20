-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema bolao
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema bolao
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `bolao` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci ;
USE `bolao` ;

-- -----------------------------------------------------
-- Table `bolao`.`usuario`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `bolao`.`usuario` (
  `email` VARCHAR(45) NOT NULL,
  `senha` VARCHAR(100) NOT NULL,
  `nome` VARCHAR(45) NOT NULL,
  `sobrenome` VARCHAR(45) NOT NULL,
  `telefone` VARCHAR(15) NOT NULL,
  PRIMARY KEY (`email`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `bolao`.`campeonato`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `bolao`.`campeonato` (
  `idcampeonato` INT NOT NULL,
  `nome` VARCHAR(45) NOT NULL,
  `emblema` VARCHAR(100) NULL DEFAULT NULL,
  PRIMARY KEY (`idcampeonato`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `bolao`.`time`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `bolao`.`time` (
  `idtime` INT NOT NULL,
  `nome` VARCHAR(45) NOT NULL,
  `escudo` VARCHAR(100) NULL DEFAULT NULL,
  PRIMARY KEY (`idtime`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `bolao`.`partida`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `bolao`.`partida` (
  `idpartida` INT NOT NULL,
  `data` DATE NOT NULL,
  `horario` TIME NOT NULL,
  `id_time_casa` INT NOT NULL,
  `num_gols_casa` INT NOT NULL,
  `id_time_fora` INT NOT NULL,
  `num_gols_fora` INT NOT NULL,
  `Campeonato_id` INT NOT NULL,
  PRIMARY KEY (`idpartida`),
  INDEX `fk_Partida_Time1_idx` (`id_time_casa` ASC) VISIBLE,
  INDEX `fk_Partida_Time2_idx` (`id_time_fora` ASC) VISIBLE,
  INDEX `fk_Partida_Campeonato1_idx` (`Campeonato_id` ASC) VISIBLE,
  CONSTRAINT `fk_Partida_Campeonato1`
    FOREIGN KEY (`Campeonato_id`)
    REFERENCES `bolao`.`campeonato` (`idcampeonato`)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT,
  CONSTRAINT `fk_Partida_Time1`
    FOREIGN KEY (`id_time_casa`)
    REFERENCES `bolao`.`time` (`idtime`),
  CONSTRAINT `fk_Partida_Time2`
    FOREIGN KEY (`id_time_fora`)
    REFERENCES `bolao`.`time` (`idtime`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `bolao`.`aposta`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `bolao`.`aposta` (
  `Apostador_email` VARCHAR(45) NOT NULL,
  `Partida_id` INT NOT NULL,
  `gols_time_visitante` INT NOT NULL,
  `gols_time_casa` INT NOT NULL,
  `data` DATE NOT NULL,
  `horario` TIME NOT NULL,
  PRIMARY KEY (`Partida_id`, `Apostador_email`),
  INDEX `fk_Usuário_has_Partida_Partida1_idx` (`Partida_id` ASC) VISIBLE,
  INDEX `fk_aposta_Apostador1_idx` (`Apostador_email` ASC) VISIBLE,
  CONSTRAINT `fk_aposta_Apostador1`
    FOREIGN KEY (`Apostador_email`)
    REFERENCES `bolao`.`usuario` (`email`),
  CONSTRAINT `fk_Usuário_has_Partida_Partida1`
    FOREIGN KEY (`Partida_id`)
    REFERENCES `bolao`.`partida` (`idpartida`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `bolao`.`bolao`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `bolao`.`bolao` (
  `idbolao` INT NOT NULL AUTO_INCREMENT,
  `nome` VARCHAR(45) NOT NULL,
  `privacidade` VARCHAR(45) NOT NULL,
  `status` TINYINT NOT NULL,
  `aposta_minima` DOUBLE NOT NULL,
  `Campeonato_id` INT NOT NULL,
  `Administrador_email` VARCHAR(45) NOT NULL,
  `placar_certo` DOUBLE NOT NULL,
  `gols_time_vencedor` DOUBLE NOT NULL,
  `gols_time_perdedor` DOUBLE NOT NULL,
  `saldo_gols` DOUBLE NOT NULL,
  `acerto_vencedor` DOUBLE NOT NULL,
  `acerto_empate` DOUBLE NOT NULL,
  PRIMARY KEY (`idbolao`),
  INDEX `fk_Bolão_Campeonato1_idx` (`Campeonato_id` ASC) VISIBLE,
  INDEX `fk_bolao_1_idx` (`Administrador_email` ASC) VISIBLE,
  CONSTRAINT `fk_bolao_1`
    FOREIGN KEY (`Administrador_email`)
    REFERENCES `bolao`.`usuario` (`email`),
  CONSTRAINT `fk_Bolão_Campeonato1`
    FOREIGN KEY (`Campeonato_id`)
    REFERENCES `bolao`.`campeonato` (`idcampeonato`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `bolao`.`participa`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `bolao`.`participa` (
  `Apostador_email` VARCHAR(45) NOT NULL,
  `Bolao_id` INT NOT NULL,
  `valor_apostado` DOUBLE NOT NULL,
  `status` CHAR(1) NOT NULL,
  PRIMARY KEY (`Bolao_id`, `Apostador_email`),
  INDEX `fk_Usuário_has_Bolão_Bolão1_idx` (`Bolao_id` ASC) VISIBLE,
  INDEX `fk_participa_Apostador1_idx` (`Apostador_email` ASC) VISIBLE,
  CONSTRAINT `fk_participa_Apostador1`
    FOREIGN KEY (`Apostador_email`)
    REFERENCES `bolao`.`usuario` (`email`),
  CONSTRAINT `fk_Usuário_has_Bolão_Bolão1`
    FOREIGN KEY (`Bolao_id`)
    REFERENCES `bolao`.`bolao` (`idbolao`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `bolao`.`possui`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `bolao`.`possui` (
  `Campeonato_id` INT NOT NULL,
  `Time_id` INT NOT NULL,
  PRIMARY KEY (`Campeonato_id`, `Time_id`),
  INDEX `fk_Campeonato_has_Time_Time1_idx` (`Time_id` ASC) VISIBLE,
  INDEX `fk_Campeonato_has_Time_Campeonato1_idx` (`Campeonato_id` ASC) VISIBLE,
  CONSTRAINT `fk_Campeonato_has_Time_Campeonato1`
    FOREIGN KEY (`Campeonato_id`)
    REFERENCES `bolao`.`campeonato` (`idcampeonato`),
  CONSTRAINT `fk_Campeonato_has_Time_Time1`
    FOREIGN KEY (`Time_id`)
    REFERENCES `bolao`.`time` (`idtime`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
