// Dain Harmon 2020/12/14
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include "open_spiel/games/futlol.h"

#include <algorithm>
#include <memory>
#include <utility>
#include <vector>

#include "open_spiel/spiel_utils.h"
#include "open_spiel/utils/tensor_view.h"

namespace open_spiel {
namespace futlol {
namespace {

// Facts about the game.
const GameType kGameType{
    /*short_name=*/"futlol",
    /*long_name=*/"Futlol",
    GameType::Dynamics::kSequential,
    GameType::ChanceMode::kDeterministic,
    GameType::Information::kPerfectInformation,
    GameType::Utility::kGeneralSum,
    GameType::RewardModel::kRewards,
    /*max_num_players=*/6,
    /*min_num_players=*/6,
    /*provides_information_state_string=*/true,
    /*provides_information_state_tensor=*/false,
    /*provides_observation_string=*/true,
    /*provides_observation_tensor=*/true,
    /*parameter_specification=*/
    {{"P0Self", GameParameter(1.0)},
    {"P0Team", GameParameter(1.0)},
    {"P1Self", GameParameter(1.0)},
    {"P1Team", GameParameter(1.0)},
    {"P2Self", GameParameter(1.0)},
    {"P2Team", GameParameter(1.0)},
    {"P3Self", GameParameter(1.0)},
    {"P3Team", GameParameter(1.0)},
    {"P4Self", GameParameter(1.0)},
    {"P4Team", GameParameter(1.0)},
    {"P5Self", GameParameter(1.0)},
    {"P5Team", GameParameter(1.0)},
    {"P6Self", GameParameter(1.0)},
    {"P6Team", GameParameter(1.0)},
    {"P7Self", GameParameter(1.0)},
    {"P7Team", GameParameter(1.0)},
    {"P8Self", GameParameter(1.0)},
    {"P8Team", GameParameter(1.0)},
    {"P9Self", GameParameter(1.0)},
    {"P9Team", GameParameter(1.0)},
    {"P10Self", GameParameter(1.0)},
    {"P10Team", GameParameter(1.0)},
    {"P11Self", GameParameter(1.0)},
    {"P11Team", GameParameter(1.0)},
    {"P12Self", GameParameter(1.0)},
    {"P12Team", GameParameter(1.0)},
    {"P13Self", GameParameter(1.0)},
    {"P13Team", GameParameter(1.0)},
    {"P14Self", GameParameter(1.0)},
    {"P14Team", GameParameter(1.0)},
    {"P15Self", GameParameter(1.0)},
    {"P15Team", GameParameter(1.0)},
    {"OddWinOnly", GameParameter(false)},
    {"EvenWinOnly", GameParameter(false)},
    }  // team/individual weights
};

std::shared_ptr<const Game> Factory(const GameParameters& params) {
  return std::shared_ptr<const Game>(new FutlolGame(params));
}

REGISTER_SPIEL_GAME(kGameType, Factory);

}  // namespace

CellState PlayerToState(Player player) {
  if (player<kNumPlayers)
  {
    return (CellState)player;
  }
  else
  {
    SpielFatalError(absl::StrCat("Invalid player id ", player));
    return CellState::kEmpty;
  }
}

std::string StateToString(CellState state) {
  switch (state) {
    case CellState::kEmpty:
      return ".";
    case CellState::kAGoal:
      return "=";
    case CellState::kBGoal:
      return "=";
    case CellState::kP0:
      return "0";
    case CellState::kP1:
      return "1";
    case CellState::kP2:
      return "2";
    case CellState::kP3:
      return "3";
    case CellState::kP4:
      return "4";
    case CellState::kP5:
      return "5";
    case CellState::kP6:
      return "6";
    case CellState::kP7:
      return "7";
    case CellState::kP8:
      return "8";
    case CellState::kP9:
      return "9";
    case CellState::kP10:
      return "A";
    case CellState::kP11:
      return "B";
    case CellState::kP12:
      return "C";
    case CellState::kP13:
      return "D";
    case CellState::kP14:
      return "E";
    case CellState::kP15:
      return "F";
    default:
      SpielFatalError("Unknown state.");
  }
}

void FutlolState::DoApplyAction(Action move) {
  
  int moveCode=move>>(cellSize);
  const FutlolGame& parent_game = static_cast<const FutlolGame&>(*game_);
  double teamReward [2]={0};
  for(int i=0; i<kNumPlayers; i++)
    rewards_[i]=0;
  if (moveCode>=16)
  {
    //resetpiece
    board_[(current_player_%2) * (kNumRows-1) * kNumCols + (moveCode-16)]=PlayerToState(current_player_);
    moves_[current_player_]++;
    rewards_[current_player_]+=kMoveValue/kMaxUtil*parent_game.self_weight_[current_player_];
  }
  else
  {
    //get the start and end of move
    int startR=-1;
    int startC=-1;
    for (int row = 0; row < kNumRows; ++row)
      for (int column = 0; column < kNumCols; ++column)
        if (board_[row * kNumCols + column] == PlayerToState(current_player_))
        {
          startR=row;
          startC=column;
        }
    int start=startR * kNumCols + startC;
    int target=-1;
    switch (moveCode)
    {
      case 0:
        target=(startR-1) * kNumCols + (startC-1);
        break;
      case 1:
        target=(startR-1) * kNumCols + (startC);
        break;
      case 2:
        target=(startR-1) * kNumCols + (startC+1);
        break;
      case 3:
        target=(startR) * kNumCols + (startC-1);
        break;
      case 4:
        target=(startR) * kNumCols + (startC);
        break;
      case 5:
        target=(startR) * kNumCols + (startC+1);
        break;
      case 6:
        target=(startR+1) * kNumCols + (startC-1);
        break;
      case 7:
        target=(startR+1) * kNumCols + (startC);
        break;
      case 8:
        target=(startR+1) * kNumCols + (startC+1);
        break;
      default:
        target=(startR) * kNumCols + (startC);
        break;
    }
    
    if(target==start)
    {
      //Do Nothing move
    }
    else
    {
      if(board_[target] == CellState::kEmpty)
      {
        moves_[current_player_]++;
        board_[target] = PlayerToState(CurrentPlayer());
        rewards_[current_player_]+=kMoveValue/kMaxUtil*parent_game.self_weight_[current_player_];
      }
      else if(board_[target] == CellState::kAGoal)
      {
        moves_[current_player_]++;
        if(current_player_%2==0)
        {
          board_[target] = PlayerToState(CurrentPlayer());
          rewards_[current_player_]+=kMoveValue/kMaxUtil*parent_game.self_weight_[current_player_];
        }
        else
        {
          goals_[current_player_]++;
          oddTeamScore_++;
          rewards_[current_player_]+=kGoalValue/kMaxUtil*parent_game.self_weight_[current_player_];
          teamReward[current_player_%2]+=kGoalValue/kMaxUtil;
        }
      }
      else if(board_[target] == CellState::kBGoal)
      {
        moves_[current_player_]++;
        if(current_player_%2==1)
        {
          board_[target] = PlayerToState(CurrentPlayer());
          rewards_[current_player_]+=kMoveValue/kMaxUtil*parent_game.self_weight_[current_player_];
        }
        else
        {
          goals_[current_player_]++;
          evenTeamScore_++;
          rewards_[current_player_]+=kGoalValue/kMaxUtil*parent_game.self_weight_[current_player_];
          teamReward[current_player_%2]+=kGoalValue/kMaxUtil;
        }
      }
      else
      {
        rewards_[current_player_]+=kCaptureValue/kMaxUtil*parent_game.self_weight_[current_player_];
        teamReward[current_player_%2]+=kCaptureValue/kMaxUtil;
        rewards_[(int)board_[target]]+=kCapturedValue/kMaxUtil*parent_game.self_weight_[(int)board_[target]];
        teamReward[(int)board_[target]%2]+=kCapturedValue/kMaxUtil;

        moves_[current_player_]++;
        timesCaptured_[(int)board_[target]]++;
        captures_[current_player_]++;
        board_[target] = PlayerToState(CurrentPlayer());
      }
      //clear old space.
      if(start/kNumCols==0)
        board_[start] = CellState::kAGoal;
      else if(start/kNumCols==kNumRows-1)
        board_[start] = CellState::kBGoal;
      else
        board_[start] = CellState::kEmpty;
    }
  }
  for(int i=0; i<kNumPlayers; i++)
    if(((i%2==1)&&parent_game.oddWinOnly)||((i%2==0)&&parent_game.evenWinOnly))
    {
      rewards_[i]=0;
      teamReward[i%2]=0;
    }

  if (oddTeamScore_>=scoreTarget||evenTeamScore_>=scoreTarget) {
    outcome_ = current_player_;
    teamReward[current_player_%2]+=kWinValue/kMaxUtil;
  }

  for(int i=0; i<kNumPlayers; i++)
  {
    rewards_[i]+=teamReward[i%2]*parent_game.team_weight_[i];
    returns_[i]+=rewards_[i];
  }

  current_player_ = (current_player_+1)%kNumPlayers;
  num_turns_ += 1;
}

std::vector<Action> FutlolState::LegalActions() const {
  if (IsTerminal()) return {};
  std::vector<Action> moves;

  //Generate 8 nieghbors
  int playerRow=-1;
  for (int row = 0; row < kNumRows; ++row) {
    for (int column = 0; column < kNumCols; ++column) {
      if (board_[row * kNumCols + column] == PlayerToState(current_player_))
      {
        playerRow=row;
        //above
        if(row>0)
        {
          //left
          if(column>0)
            moves.push_back((0<<cellSize)+(int)board_[(row-1) * kNumCols + (column-1)]);

          moves.push_back((1<<cellSize)+(int)board_[(row-1) * kNumCols + column]);

          //right
          if(column<kNumCols-1)
            moves.push_back((2<<cellSize)+(int)board_[(row-1) * kNumCols + (column+1)]);
        }
        
        //left
        if(column>0)
          moves.push_back((3<<cellSize)+(int)board_[row * kNumCols + (column-1)]);

        //stay
        moves.push_back((4<<cellSize)+(int)board_[row * kNumCols + column]);

        //right
        if(column<kNumCols-1)
          moves.push_back((5<<cellSize)+(int)board_[row * kNumCols + (column+1)]);

        //below
        if(row<kNumRows-1)
        {
          //left
          if(column>0)
            moves.push_back((6<<cellSize)+(int)board_[(row+1) * kNumCols + (column-1)]);

          moves.push_back((7<<cellSize)+(int)board_[(row+1) * kNumCols + column]);

          //right
          if(column<kNumCols-1)
            moves.push_back((8<<cellSize)+(int)board_[(row+1) * kNumCols + (column+1)]);
        }
      }
    }
  }
  if(moves.size()==0)
  {
    for(int column = 0; column < kNumCols; ++column)
      moves.push_back(((16+column)<<cellSize)+(int)board_[(current_player_%2) * (kNumRows-1) * kNumCols + column]);
  }

  //Filter invalid
  std::vector<Action> finalMoves;
  for(auto move: moves)
  {
    CellState destCell=(CellState)(move&((1<<cellSize)-1));
    if((int)destCell==(int)current_player_)
      finalMoves.push_back(move);
    else if(destCell==CellState::kEmpty)
      finalMoves.push_back(move);
    else if (destCell==CellState::kAGoal)
      finalMoves.push_back(move);
    else if (destCell==CellState::kBGoal)
      finalMoves.push_back(move);
    else if (current_player_%2==0&&(int)destCell%2==1&&playerRow<kNumRows/2)
      finalMoves.push_back(move);
    else if (current_player_%2==1&&(int)destCell%2==0&&playerRow>=kNumRows/2)
      finalMoves.push_back(move);
  }
  return finalMoves;
}

std::string FutlolState::ActionToString(Player player, Action action_id) const {
  int moveCode=action_id>>(cellSize);
  if(moveCode>=16)
  {
    return absl::StrCat(StateToString(PlayerToState(player)), " Spawns at col: ",
                      moveCode-16);
  }
  else
  {
    switch (moveCode)
    {
      case 0:
        return absl::StrCat(StateToString(PlayerToState(player)), " moves up-left");
        break;
      case 1:
        return absl::StrCat(StateToString(PlayerToState(player)), " moves up");
        break;
      case 2:
        return absl::StrCat(StateToString(PlayerToState(player)), " moves up-right");
        break;
      case 3:
        return absl::StrCat(StateToString(PlayerToState(player)), " moves left");
        break;
      case 4:
        return absl::StrCat(StateToString(PlayerToState(player)), " stays");
        break;
      case 5:
        return absl::StrCat(StateToString(PlayerToState(player)), " moves right");
        break;
      case 6:
        return absl::StrCat(StateToString(PlayerToState(player)), " moves down-left");
        break;
      case 7:
        return absl::StrCat(StateToString(PlayerToState(player)), " moves down");
        break;
      case 8:
        return absl::StrCat(StateToString(PlayerToState(player)), " moves down-right");
        break;
      default:
        return absl::StrCat(StateToString(PlayerToState(player)), " stays");
        break;
    }
    return absl::StrCat(StateToString(PlayerToState(player)), " stays");
  }
}

FutlolState::FutlolState(std::shared_ptr<const Game> game) : State(game) {
  std::fill(begin(board_), begin(board_)+kNumCols, CellState::kAGoal);
  std::fill(begin(board_)+kNumCols, end(board_)-kNumCols, CellState::kEmpty);
  std::fill(end(board_)-kNumCols, end(board_), CellState::kBGoal);
}

std::string FutlolState::ToString() const {
  std::string str;
  absl::StrAppend(&str, evenTeamScore_,", ");
  absl::StrAppend(&str, oddTeamScore_,", ");
  for (int i = 0; i < kNumPlayers; ++i)
    absl::StrAppend(&str, captures_[i],", ");
  for (int i = 0; i < kNumPlayers; ++i)
    absl::StrAppend(&str, timesCaptured_[i],", ");
  for (int i = 0; i < kNumPlayers; ++i)
    absl::StrAppend(&str, goals_[i],", ");
  for (int i = 0; i < kNumPlayers; ++i)
    absl::StrAppend(&str, moves_[i],", ");
  absl::StrAppend(&str, "\n");

  for (int r = 0; r < kNumRows; ++r) {
    for (int c = 0; c < kNumCols; ++c) {
      absl::StrAppend(&str, StateToString(BoardAt(r, c)));
    }
    if (r < (kNumRows - 1)) {
      absl::StrAppend(&str, "\n");
    }
  }
  return str;
}

bool FutlolState::IsTerminal() const {
  return outcome_ != kInvalidPlayer || oddTeamScore_>=scoreTarget||evenTeamScore_>=scoreTarget;
}

std::string FutlolState::InformationStateString(Player player) const {
  SPIEL_CHECK_GE(player, 0);
  SPIEL_CHECK_LT(player, num_players_);
  return HistoryString();
}

std::string FutlolState::ObservationString(Player player) const {
  SPIEL_CHECK_GE(player, 0);
  SPIEL_CHECK_LT(player, num_players_);
  return ToString();
}

void FutlolState::ObservationTensor(Player player,
                                       absl::Span<float> values) const {
  SPIEL_CHECK_GE(player, 0);
  SPIEL_CHECK_LT(player, num_players_);

  // Treat `values` as a 2-d tensor.
  TensorView<2> view(values, {kCellStates, kNumCells}, true);
  for (int cell = 0; cell < kNumCells; ++cell) {
    view[{static_cast<int>(board_[cell]), cell}] = 1.0;
  }
}

/*void FutlolState::UndoAction(Player player, Action move) {
  int moveCode=move>>(cellSize);
  CellState destCell=(CellState)(move&((1<<cellSize)-1));
  if(moveCode>=16)
  {
    board_[(current_player_%2) * (kNumRows-1) * kNumCols + (moveCode-16)]=destCell;
    moves_[player]--;
  }
  else
  {
    //get the start and end of move
    int startR=-1;
    int startC=-1;
    for (int row = 0; row < kNumRows; ++row)
      for (int column = 0; column < kNumCols; ++column)
        if (board_[row * kNumCols + column] == PlayerToState(player))
        {
          startR=row;
          startC=column;
        }
    int target=startR * kNumCols + startC;
    int start=-1;
    switch (moveCode)
    {
      case 0:
        start=(startR+1) * kNumCols + (startC+1);
        break;
      case 1:
        start=(startR+1) * kNumCols + (startC);
        break;
      case 2:
        start=(startR+1) * kNumCols + (startC-1);
        break;
      case 3:
        start=(startR) * kNumCols + (startC+1);
        break;
      case 4:
        start=(startR) * kNumCols + (startC);
        break;
      case 5:
        start=(startR) * kNumCols + (startC-1);
        break;
      case 6:
        start=(startR-1) * kNumCols + (startC+1);
        break;
      case 7:
        start=(startR-1) * kNumCols + (startC);
        break;
      case 8:
        start=(startR-1) * kNumCols + (startC-1);
        break;
      default:
        start=(startR) * kNumCols + (startC);
        break;
    }
    board_[start] = PlayerToState(player);

    if(start!=target)
    {
      moves_[player]--;
      board_[target] = destCell;
    }

    if(destCell==CellState::kAGoal&&player%2==1)
    {
      goals_[player]--;
      oddTeamScore_--;
    }
    else if(destCell==CellState::kBGoal&&player%2==0)
    {
      goals_[player]--;
      evenTeamScore_--;
    }
    else if((int)destCell<16&&(int)destCell!=player)
    {
      timesCaptured_[(int)destCell]--;
      captures_[player]--;
    }
  }

  current_player_ = player;
  outcome_ = kInvalidPlayer;
  num_turns_ -= 1;
  history_.pop_back();
}*/

std::unique_ptr<State> FutlolState::Clone() const {
  return std::unique_ptr<State>(new FutlolState(*this));
}

FutlolGame::FutlolGame(const GameParameters& params)
    : Game(kGameType, params)
    
     {
       for(int i=0; i<kNumPlayers; i++)
       {
        self_weight_[i]=ParameterValue<double>(absl::StrCat("P",i,"Self"));
        team_weight_[i]=ParameterValue<double>(absl::StrCat("P",i,"Team"));
       }
       oddWinOnly=ParameterValue<bool>("OddWinOnly");
       evenWinOnly=ParameterValue<bool>("EvenWinOnly");
     }

}  // namespace futlol
}  // namespace open_spiel
